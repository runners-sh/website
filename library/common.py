# common.py -- code not ubiquitous enough to go in library/__init__.py but contains shared functionality across the sites

from library import *

def do_markdown_ssg():
    for dirname, dirs, files in os.walk("content"):
        for file in files:
            name, ext = path.splitext(file)
            if ext != ".md": continue
            src_path = path.join(dirname, file)
            dist_path = path.join(dirname, name + ".html")
            with LogTimer(f"Markdown process {src_path} -> {dist_path}"):
                meta, content = markdown_to_html(src_path)
                page(
                    "blog.html",
                    dist_path,
                    content=content,
                    title=meta.get("title")
                )

    if path.exists("public"):
        with LogTimer(f"Copying public files"):
            shutil.copytree("public", dist_path_for("public"))

__all__ = [
    "do_markdown_ssg"
]
