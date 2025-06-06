from os import path

from runners_common import funbar
from solstice import *

ssg = SiteGenerator(output_path="../dist/main-site")

@cli.entrypoint(ssg)
def build():
	ssg.copy("public")
	ascii_logo = read_file("ascii/logo.asc")
	ascii_name = read_file("ascii/name.asc")
	ssg.page("index.jinja", ascii_logo=ascii_logo, ascii_name=ascii_name)

	posts = []

	# TODO: this will detect files that collide in main-site but not others
	# currently all the barcodes are in main-site so this is fine but once we make projects.runners.sh or zine.runners.sh this will need to be changed
	barcode_set = {}

	for dirname, file, name, _ in recurse_files("blog", [".md"]):
		src_path = path.join(dirname, file)
		dist_path = path.join(dirname, name + ".html")
		with MarkdownPage(ssg, "blog.jinja", src_path, dist_path) as pg:
			posts.append(
				pg.meta | {"url": "/" + dist_path.removesuffix(".html")}
			)

			barcode = pg.meta.get("barcode")
			if barcode is not None:
				funbar.get_barcode_cache(ssg.output_path).add(barcode)
				if orig_page := barcode_set.get(barcode):
					raise Exception(
						f"duplicate barcode for pages {orig_page} and {src_path}: {barcode}"
					)
				barcode_set[barcode] = src_path
			if barcode is None:
				warn(
					f"Barcode not provided for {src_path}, using dummy barcode"
				)
				barcode = 69
			pg.set_params(funbar=funbar.html_from_ean8(barcode))

	posts.sort(key=lambda x: x["date"], reverse=True)

	ssg.page("blog-overview.jinja", "blog/index.html", posts=posts)
