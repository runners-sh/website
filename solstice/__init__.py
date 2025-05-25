import os
import os.path as path
import shutil

import frontmatter
import jinja2
import markdown

from .log import *

pkgname: str
env: jinja2.Environment
base_path: str
dist_path: str


def init(package_name: str | None):
	global pkgname, env, base_path, dist_path

	timer = LogTimer(
		f"Building {package_name!r}", f"Finished {package_name!r} in {{}}"
	)
	timer.__enter__()
	import atexit

	atexit.register(timer.__exit__)

	# to satisfy type checking
	assert package_name is not None
	pkgname = package_name

	module_path = __import__(package_name).__path__[0]
	os.chdir(module_path)

	while module_path != "/":
		if path.exists(path.join(module_path, ".git")):
			break
		module_path = path.dirname(module_path)
	base_path = module_path
	dist_path = path.join(base_path, "dist")

	shutil.rmtree(dist_path, ignore_errors=True)

	env = jinja2.Environment(
		loader=jinja2.PackageLoader(package_name), autoescape=True
	)


def dist_path_for(name: str) -> str:
	p = path.join(dist_path, pkgname, name)
	dirname = path.dirname(p)
	os.makedirs(dirname, exist_ok=True)
	return p


def page(template_name: str, output_path: str | None = None, **kwargs):
	"""
	Generate a page from a Jinja2 template.
	# Arguments
	- `template_name`: Name of the template to use.
	- `output_path`: Path to save the rendered HTML file to. Defaults to the template name.
	- `**kwargs`: Additional keyword arguments to pass to the template.
	"""
	with open(dist_path_for(output_path or template_name), "w") as file:
		contents = env.get_template(template_name).render(**kwargs)
		file.write(contents)


def page_md(
	template_name: str,
	content_path: str,
	output_path: str | None = None,
	**kwargs,
):
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
	with LogTimer(
		f"Markdown process {content_path} -> {output_path}",
		f"Finished building '{output_path}' in {{}}",
	):
		meta, content = load_markdown(content_path)
		for key, val in kwargs.items():
			if key in meta.keys():
				warn(f"(in content file '{content_path}'):")
				warn(f"\tkey '{key}' is reserved by the caller, skipping...")
			meta[key] = val

		if "content" in meta.keys():
			warn(f"(in content file '{content_path}'):")
			warn("\tkey 'content' is reserved, skipping...")
			meta.pop("content")

		page("blog.html", output_path, content=content, **meta)


def recurse_files(root: str, extensions: list[str]):
	"""
	Recursively find files in a directory with specified extensions.

	# Arguments
	- `root`: The root directory to start searching from.
	- `extensions`: A list of file extensions to filter by (e.g., ['.md', '.txt']).

	# Yields
	Tuples of (directory name, file name, file base name) for each matching file.
	"""
	for dirname, dirs, files in os.walk(root):
		for file in files:
			name, ext = path.splitext(file)
			if ext not in extensions:
				continue
			yield (dirname, file, name)


def copy(dir: str):
	"""
	Copy a directory to the output path, without altering its contents.
	Used for copying static assets like images, CSS, etc.
	# Arguments
	- `dir`: The directory to copy.
	"""
	if path.exists(dir):
		with LogTimer(f"Copying directory '{dir}'"):
			shutil.copytree(dir, dist_path_for(dir))


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
		return meta, markdown.markdown(
			content,
			extensions=[
				"markdown.extensions.extra",
				"markdown.extensions.admonition",
				"markdown.extensions.codehilite",
			],
		)


from . import common  # noqa: E402 F401
