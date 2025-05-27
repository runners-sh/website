from typing import Any

from solstice import *

init(__package__)

copy("public")

ascii_logo = common.read_file("ascii/logo.asc")
ascii_name = common.read_file("ascii/name.asc")
page("index.jinja", ascii_logo=ascii_logo, ascii_name=ascii_name)

for dirname, file, name, _ in recurse_files("blog", [".md"]):
	src_path = path.join(dirname, file)
	dist_path = path.join(dirname, name + ".html")
	with MarkdownPage("blog.jinja", src_path, dist_path) as page:
		if not page.cached:
			page_id: Any = page.meta.get("id")
			page.template_params(funbar=funbar.funbar_html_from_seed(page_id))


finalize()
