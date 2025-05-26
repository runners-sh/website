from solstice import *
from solstice.common import load_verbatim

init(__package__)
copy("public")

ascii_logo = load_verbatim("ascii/logo.asc")
ascii_name = load_verbatim("ascii/name.asc")
page("index.jinja", ascii_logo=ascii_logo, ascii_name=ascii_name)

for dirname, file, name in recurse_files("content", [".md"]):
	src_path = path.join(dirname, file)
	dist_path = path.join(dirname, name + ".html")
	page_md("blog.jinja", src_path, dist_path)
