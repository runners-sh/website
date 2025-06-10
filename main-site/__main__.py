from os import path

from runners_common import funbar
from solstice import *

ssg = SiteGenerator(output_path="../dist/main-site")


def build_blog(ssg) -> list[dict]:
	posts = []

	# TODO: this will detect files that collide in main-site but not others
	# currently all the barcodes are in main-site so this is fine but once we make projects.runners.sh or zine.runners.sh this will need to be changed
	barcode_set = {}

	for dirname, file, name, _ in recurse_files("blog", [".md"]):
		src_path = path.join(dirname, file)
		dist_path = path.join(dirname, name + ".html")
		with MarkdownPage(ssg, "blog.jinja", src_path, dist_path) as pg:
			if not pg.meta.get("hidden", False):
				posts.append(pg.meta | {"url": "/" + dist_path.removesuffix(".html")})

			barcode = pg.meta.get("barcode")
			if barcode is not None:
				funbar.get_barcode_cache(ssg.output_path).add(barcode)
				if orig_page := barcode_set.get(barcode):
					raise Exception(
						f"duplicate barcode for pages {orig_page} and {src_path}: {barcode}"
					)
				barcode_set[barcode] = src_path
			if barcode is None:
				warn(f"Barcode not provided for {src_path}, using dummy barcode")
				barcode = 69
			pg.set_params(funbar=funbar.html_from_ean8(barcode))

	posts.sort(key=lambda x: x["date"], reverse=True)
	ssg.page("blog-overview.jinja", "blog/index.html", posts=posts)

	return posts


social_link_formats = {
	"github": "https://github.com/{}",
	"mastodon": "https://mastodon.social/@{}",
	"bsky": "https://bsky.app/profile/{}",
	"website": "https://{}",
}

social_link_icons = {
	"github": "icon/github.svg",
	"mastodon": "icon/mastodon.svg",
	"bsky": "icon/bsky.svg",
	"website": "icon/globe.svg",
}


def build_members(ssg, posts) -> list[dict]:
	members = []

	for dirname, file, name, _ in recurse_files("member", [".md"]):
		src_path = path.join(dirname, file)
		dist_path = path.join(dirname, name + ".html")
		with MarkdownPage(ssg, "member.jinja", src_path, dist_path) as pg:
			links = [
				{
					"type": k,
					"name": v,
					"url": social_link_formats[k].format(v),
					"icon": social_link_icons[k],
				}
				for k, v in pg.meta["links"].items()
			]
			links.sort(key=lambda x: x["name"])

			if not pg.meta.get("pfp"):
				pg.set_params(pfp=f"/public/pfp/{name}.avif")
			pg.set_params(link_data=links, username=name)

			members.append(pg.meta | {"url": "/" + dist_path.removesuffix(".html")})

	return members


@cli.entrypoint(ssg, extra_watches=["../runners_common", "../solstice"])
def build():
	ssg.copy("public")
	ascii_logo = read_file("ascii/logo.asc")
	ascii_name = read_file("ascii/name.asc")
	ssg.page("index.jinja", ascii_logo=ascii_logo, ascii_name=ascii_name)

	posts = build_blog(ssg)
	_members = build_members(ssg, posts)
