from library import *

init(__package__)

page("base.html")

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
                title=meta["title"]
            )
