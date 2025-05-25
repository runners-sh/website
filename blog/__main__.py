from solstice import *

init(__package__)
copy("public")
page("index.html")

for dirname, file, name in recurse_files("content", [".md"]):
	src_path = path.join(dirname, file)
	dist_path = path.join(dirname, name + ".html")
	page_md("blog.html", src_path, dist_path)