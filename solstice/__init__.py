# ruff: noqa: F401 E402
# pyright: reportMissingImports=false, reportMissingModuleSource=false

import os
import os.path as path
import shutil
from argparse import Namespace
from typing import Literal

import frontmatter
import jinja2
import markdown

from . import (
	common,
	funbar,
)
from .log import *
from .minify import *

pkgname: str
env: jinja2.Environment
module_path: str
dist_path: str
profile: Literal["dev", "prod"] = "dev"


def init(package_name: str | None):
	global pkgname, env, module_path, dist_path

	# to satisfy type checking
	assert package_name is not None
	pkgname = package_name

	module_path = __import__(package_name).__path__[0]
	os.chdir(module_path)

	base_path = module_path
	while base_path != "/":
		if path.exists(path.join(base_path, "pyproject.toml")):
			break
		base_path = path.dirname(base_path)
	dist_path = path.join(base_path, "dist", package_name)

	from . import cli

	cli.run_cli()

	env = jinja2.Environment(loader=jinja2.PackageLoader(package_name), autoescape=True)
	env.globals["profile"] = profile


def dist_path_for(name: str) -> str:
	p = path.join(dist_path, name)
	dirname = path.dirname(p)
	os.makedirs(dirname, exist_ok=True)
	return p


def page(template_name: str, output_path: str | None = None, **kwargs):
	global cli_args
	"""
	Generate a page from a Jinja2 template.
	# Arguments
	- `template_name`: Name of the template to use.
	- `output_path`: Path to save the rendered HTML file to. Defaults to the template name.
	- `**kwargs`: Additional keyword arguments to pass to the template.
	"""
	dist_path = dist_path_for(output_path or (path.splitext(template_name)[0] + ".html"))
	with open(dist_path, "w") as file:
		contents = env.get_template(template_name).render(kwargs)
		file.write(contents)
	return dist_path


def finalize():
	if profile == "prod":
		_minify_all()


def _minify_all():
	with LogTimer("Minifying files..."):
		for dirname, file, name, ext in recurse_files(dist_path, [".css", ".html", ".js"]):
			with open(path.join(dirname, file), "r+") as f:
				contents = f.read()
				match ext:
					case ".html":
						contents = minify_html(contents)
				f.seek(0)
				f.write(contents)
				f.truncate()


class MarkdownPage:
	"""
	Generate a page from a markdown file with frontmatter metadata.
	# Arguments
	- `template_name`: Name of the template to use.
	- `content_path`: Path to the markdown file to insert into the template.
	- `output_path`: Path to save the rendered HTML file to. Defaults to the template name.
	- `**kwargs`: Additional keyword arguments to pass to the template.

	# Notes
	- `**kwargs` cannot contain the `content` key, as it is reserved for the markdown content.
	- Keys from the frontmatter metadata in the markdown file will be shadowed by `**kwargs` if they overlap.
	"""

	def __init__(
		self,
		template_name: str,
		src_path: str,
		output_path: str,
	):
		self.template_name = template_name
		self.src_path = src_path
		self.output_path = output_path

		self.cached = False

		"""
		# TODO: caching implementation. currently this won't reload everything if e.g. __main__.py is modified

		src_stat = os.stat(src_path)
		try:
			out_stat = os.stat(dist_path_for(output_path))
			if out_stat.st_mtime >= src_stat.st_mtime:
				info(f"{src_path} not modified since last build")
				self.cached = True
				self.meta = frontmatter.load(src_path).metadata
				return
		except FileNotFoundError:
			pass
		"""

		self._log_timer = LogTimer(
			f"Markdown process {src_path} -> {output_path}",
			f"Finished building '{output_path}' in {{}}",
		)

		self.meta, self.content = load_markdown(src_path)

		self.params = {}

	def template_params(self, **params):
		self.params |= params

	def __enter__(self):
		if not self.cached:
			self._log_timer.__enter__()
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		if exc_value:
			return
		if not self.cached:
			self._log_timer.__exit__(exc_type, exc_value, traceback)
			self.process()

	def process(self):
		params = self.params
		for key, val in self.meta.items():
			if key in params:
				warn(f"(in content file '{self.src_path}'):")
				warn(f"\tkey '{key}' is reserved by the caller, skipping...")
			else:
				params[key] = val

		if "content" in params:
			warn(f"(in content file '{self.src_path}'):")
			warn("\tkey 'content' is reserved, skipping...")
			params.pop("content")
		page(
			self.template_name,
			self.output_path,
			content=self.content,
			toc=_markdown_instance.toc,  # type: ignore
			**params,
		)


def page_md(template_name: str, src_path: str, output_path: str, **kwargs):
	with MarkdownPage(template_name, src_path, output_path) as page:
		if kwargs and not page.cached:
			page.template_params(**kwargs)


def recurse_files(root: str, extensions: list[str]):
	"""
	Recursively find files in a directory with specified extensions.

	# Arguments
	- `root`: The root directory to start searching from.
	- `extensions`: A list of file extensions to filter by (e.g., ['.md', '.txt']).

	# Yields
	Tuples of (directory name, file name, file base name, extension) for each matching file.
	"""
	for dirname, dirs, files in os.walk(root):
		for file in files:
			name, ext = path.splitext(file)
			if ext not in extensions:
				continue
			yield (dirname, file, name, ext)


def copy(dir: str):
	"""
	Copy a directory to the output path, without altering its contents.
	Used for copying static assets like images, CSS, etc.
	# Arguments
	- `dir`: The directory to copy.
	"""
	if path.exists(dir):
		dist = dist_path_for(dir)
		with LogTimer(f"Copying directory '{dir}'"):
			shutil.copytree(dir, dist, dirs_exist_ok=True)


from pymdownx.emoji import EmojiExtension
from pymdownx.emoji import to_alt as emoji_to_alt
from pymdownx.highlight import HighlightExtension
from l2m4m import LaTeX2MathMLExtension

_markdown_instance = markdown.Markdown(
	extensions=[
		"admonition",
		"pymdownx.extra",
		"pymdownx.tilde",
		"toc",
		EmojiExtension(emoji_generator=emoji_to_alt),
		HighlightExtension(
			css_class="codehilite",
			linenums=True,
		),
		LaTeX2MathMLExtension(),
	],
)


def load_markdown(file_path: str) -> tuple[dict, str]:
	"""
	Load a markdown file with frontmatter metadata, and convert it into HTML.

	# Arguments
	- `file_path`: The path to the markdown file to load.

	# Returns
	The frontmatter metadata and the resulting html of the markdown content.
	"""
	with open(file_path, "r") as f:
		meta, content = frontmatter.parse(f.read())
		return meta, convert_markdown(content)


def convert_markdown(markdown: str) -> str:
	_markdown_instance.reset()
	return _markdown_instance.convert(markdown)
