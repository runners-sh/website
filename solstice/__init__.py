import os
import os.path as path
import atexit
import shutil

import frontmatter
import jinja2
import markdown

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
		if path.exists(path.join(base_path, ".git")):
			break
		base_path = path.dirname(base_path)
	dist_path = path.join(base_path, "dist", package_name)

	from . import cli

	cli.run_cli()

	timer = LogTimer(f"Building {package_name!r}", f"Finished {package_name!r} in {{}}")
	timer.__enter__()

	atexit.register(timer.__exit__)

	env = jinja2.Environment(loader=jinja2.PackageLoader(package_name), autoescape=True)


def dist_path_for(name: str) -> str:
	p = path.join(dist_path, name)
	dirname = path.dirname(p)
	os.makedirs(dirname, exist_ok=True)
	return p


def page(template_name: str, output_path: str | None = None, **kwargs) -> str:
	dist_path = dist_path_for(output_path or template_name)
	contents = env.get_template(template_name).render(**kwargs)
	with open(dist_path, "w") as file:
		file.write(contents)
	return dist_path


def markdown_page(
	template_name: str,
	src_path: str,
	output_path: str,
	**kwargs,
):
	src_stat = os.stat(src_path)
	try:
		out_stat = os.stat(dist_path_for(output_path))
		if out_stat.st_mtime == src_stat.st_mtime:
			info(f"{src_path} not modified since last build, ignoring")
			return
	except FileNotFoundError:
		pass

	with LogTimer(f"Markdown process {src_path} -> {output_path}"):
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


def recurse_files(root: str, extensions: list[str]):
	for dirname, dirs, files in os.walk(root):
		for file in files:
			name, ext = path.splitext(file)
			if ext not in extensions:
				continue
			yield (dirname, file, name)


def load_markdown(file_path: str) -> tuple[dict, str]:
	with open(file_path, "r") as f:
		meta, content = frontmatter.parse(f.read())
		return meta, markdown.markdown(content)


from . import common  # noqa: E402 F401
