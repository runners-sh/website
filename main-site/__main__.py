from typing import Any

from solstice import *

init(__package__)

copy("public")

ascii_logo = common.read_file("ascii/logo.asc")
ascii_name = common.read_file("ascii/name.asc")

page("index.jinja", ascii_logo=ascii_logo, ascii_name=ascii_name)

posts = []
for dirname, file, name, _ in recurse_files("blog", [".md"]):
	src_path = path.join(dirname, file)
	dist_path = path.join(dirname, name + ".html")
	with MarkdownPage("blog.jinja", src_path, dist_path) as pg:
		posts.append(pg.meta | {"url": "/" + dist_path.removesuffix(".html")})

		if not pg.cached:
			pg_id: Any = pg.meta.get("id")
			pg.template_params(funbar=funbar.funbar_html_from_seed(pg_id))

page("blog-overview.jinja", "blog/index.html", posts=posts)

finalize()
