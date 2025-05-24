# common.py -- code not ubiquitous enough to go in library/__init__.py but contains shared functionality across the sites

from solstice import *


def simple_recursive_ssg(template_name: str, content_dir: str):
	for dirname, file, name in recurse_files(content_dir, [".md"]):
		src_path = path.join(dirname, file)
		dist_path = path.join(dirname, name + ".html")
		with LogTimer(f"Markdown process {src_path} -> {dist_path}"):
			markdown_page(template_name, src_path, dist_path)

	if path.exists("public"):
		with LogTimer("Copying public files"):
			shutil.copytree("public", dist_path_for("public"))


__all__ = ["simple_recursive_ssg"]
