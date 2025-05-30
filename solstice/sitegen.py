# pyright: reportMissingImports=false, reportMissingModuleSource=false
import os
import shutil
from os import path
from typing import Any, Literal

import frontmatter
import jinja2
import markdown
from l2m4m import LaTeX2MathMLExtension
from pymdownx.emoji import EmojiExtension
from pymdownx.emoji import to_alt as emoji_to_alt
from pymdownx.highlight import HighlightExtension

from .log import LogTimer, warn

__all__ = [
	"filename_to_html",
	"read_file",
	"recurse_files",
	"SiteGenerator",
	"Page",
	"MarkdownPage",
]


def filename_to_html(name: str) -> str:
	return path.splitext(name)[0] + ".html"


def read_file(path: str) -> str:
	with open(path, "r") as file:
		return file.read()


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


class SiteGenerator:
	module_name: str
	""" Name of the current module """

	module_path: str
	""" Path to the current module directory """

	output_path: str
	""" Output directory for the site generator """

	templates_path: str
	""" Path to load the Jinja2 templates from """

	profile: Literal["dev", "prod"]
	""" Release profile. Can be 'dev' (development) or 'prod' (production) """

	jinja_env: jinja2.Environment
	""" Jinja2 environment data """

	_md_instance: markdown.Markdown

	def __init__(
		self,
		module_name: str,
		output_path: str | None = None,
		templates_path: str | None = None,
		profile: Literal["dev", "prod"] = "dev",
	):
		self.module_name = module_name

		self.module_path = __import__(module_name).__path__[0]
		os.chdir(self.module_path)

		# default to '/dist' in module directory
		self.output_path = output_path or path.join(self.module_path, "./dist")

		self.templates_path = templates_path or path.join(self.module_path, "./templates")

		self.profile = profile

		self.jinja_env = jinja2.Environment(
			loader=jinja2.FileSystemLoader(self.templates_path),
			autoescape=True,
			optimized=(self.profile == "prod"),
		)
		self.jinja_env.globals["profile"] = self.profile

		self._md_instance = markdown.Markdown(
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

	def output_path_for(self, name: str) -> str:
		p = path.join(self.output_path, name)
		dirname = path.dirname(p)
		os.makedirs(dirname, exist_ok=True)
		return p

	def render(self, name: str, **kwargs) -> str:
		return self.jinja_env.get_template(name).render(kwargs)

	def md_to_html(self, markdown: str) -> tuple[str, str]:
		self._md_instance.reset()
		content = self._md_instance.convert(markdown)
		return content, self._md_instance.toc  # type: ignore

	def load_md(self, path: str) -> tuple[str, str, dict[str, Any]]:
		with open(path, "r") as f:
			meta, content = frontmatter.parse(f.read())
			content, toc = self.md_to_html(content)
			return content, toc, meta

	def copy(self, dir: str):
		"""
		Copy a directory to the output path, without altering its contents.
		Used for copying static assets like images, CSS, etc.
		# Arguments
		- `dir`: The directory to copy.
		"""
		if path.exists(dir):
			dist = self.output_path_for(dir)
			with LogTimer(f"Copying directory '{dir}'..."):
				shutil.copytree(dir, dist, dirs_exist_ok=True)

	def clean(self):
		try:
			with LogTimer(f"Cleaning {self.output_path}"):
				shutil.rmtree(self.output_path)
		except FileNotFoundError:
			warn("Nothing to clean.")

	def page(self, template_name: str, output_path: str | None = None, **kwargs):
		with Page(self, template_name, output_path) as pg:
			pg.set_params(**kwargs)

	def markdown_page(
		self,
		template_name: str,
		content_path: str,
		output_path: str | None = None,
		**kwargs,
	):
		with MarkdownPage(self, template_name, content_path, output_path) as pg:
			pg.set_params(**kwargs)


class Page:
	def __init__(
		self,
		gen: SiteGenerator,
		template_name: str,
		output_path: str | None = None,
	):
		self.template_name = template_name
		self.output_path = output_path or filename_to_html(self.template_name)
		self.gen = gen

		self._log_timer = LogTimer(
			f"Building '{template_name}' -> '{output_path}'...",
			f"Built '{output_path}' in {{}}",
		)
		self.params = {}

	def set_params(self, **params):
		self._set_params_internal(
			"key '{}' is set multiple times.",
			**params,
		)

	def _set_params_internal(
		self,
		dup_warn: str,
		overwrite=True,
		**params,
	):
		for key, val in params.items():
			if key in self.params.keys():
				warn(dup_warn.format(key))
			else:
				self.params[key] = val

	def __enter__(self):
		self._log_timer.__enter__()
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self._log_timer.__exit__(exc_type, exc_value, traceback)
		self.build()

	def build(self):
		dest = self.gen.output_path_for(self.output_path)
		with open(dest, "w") as file:
			contents = self.gen.render(self.template_name, **self.params)
			file.write(contents)


class MarkdownPage(Page):
	def __init__(
		self,
		gen: SiteGenerator,
		template_name: str,
		content_path: str,
		output_path: str | None = None,
	):
		super().__init__(gen, template_name, output_path)
		self._log_timer = LogTimer(
			f"Building '{content_path}' -> '{output_path}'...",
			f"Built '{output_path}' in {{}}",
		)
		self.content_path = content_path
		self.content, self.toc, self.meta = self.gen.load_md(self.content_path)

	def build(self):
		self._set_params_internal(
			"frontmatter: key '{}' is already set by the caller, skipping...",
			overwrite=False,
			**self.meta,
		)
		self._set_params_internal(
			"key '{}' is reserved for markdown content.",
			content=self.content,
			toc=self.toc,
		)

		return super().build()
