from library import *

init(__package__)

page("base.html")

for dirname, dirs, files in os.walk("content"):
    for file in files:
        name, ext = path.splitext(file)
        if ext != ".md": continue
        meta, content = markdown_to_html(path.join(dirname, file))
        page(
            "blog.html",
            path.join(dirname, name + ".html"),
            content=content,
            title=meta["title"]
        )
