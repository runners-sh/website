import os
import os.path as path
import shutil

import frontmatter  # type: ignore (removes pyright hallucination)
import jinja2
import markdown  # type: ignore (removes pyright hallucination)

from .log import *

pkgname: str
env: jinja2.Environment
module_path: str
dist_path: str


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


def dist_path_for(name: str) -> str:
	p = path.join(dist_path, name)
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
	dist_path = dist_path_for(output_path or template_name)
	with open(dist_path, "w") as file:
		contents = env.get_template(template_name).render(**kwargs)
		file.write(contents)
	return dist_path


def page_md(
	template_name: str,
	src_path: str,
	output_path: str,
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

	src_stat = os.stat(src_path)
	try:
		out_stat = os.stat(dist_path_for(output_path))
		if out_stat.st_mtime == src_stat.st_mtime:
			info(f"{src_path} not modified since last build, ignoring")
			return
	except FileNotFoundError:
		pass

	with LogTimer(
		f"Markdown process {src_path} -> {output_path}",
		f"Finished building '{output_path}' in {{}}",
	):
		meta, content = load_markdown(src_path)
		for key, val in kwargs.items():
			if key in meta.keys():
				warn(f"(in content file '{src_path}'):")
				warn(f"\tkey '{key}' is reserved by the caller, skipping...")
			meta[key] = val

		if "content" in meta:
			warn(f"(in content file '{src_path}'):")
			warn("\tkey 'content' is reserved, skipping...")
			meta.pop("content")

		dist_path = page("blog.html", output_path, content=content, **meta)
		try:
			os.utime(dist_path, (src_stat.st_mtime, src_stat.st_mtime))
		except Exception:
			# can't set modification time, just ignore. caching will be unsupported on these platforms
			pass

		page(template_name, output_path, content=content, **meta)


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
			shutil.copytree(dir, dist_path_for(dir), dirs_exist_ok=True)


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
