from solstice import *

init(__package__)
copy("public")
page("index.jinja")

for dirname, file, name in recurse_files("content", [".md"]):
	src_path = path.join(dirname, file)
	dist_path = path.join(dirname, name + ".html")
	page_md("blog.jinja", src_path, dist_path)
