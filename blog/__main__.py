from solstice import *

init(__package__)
page("index.html")
common.simple_recursive_ssg("blog.html", "content")
