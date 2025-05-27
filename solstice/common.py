# common.py -- code not ubiquitous enough to go in library/__init__.py but contains shared functionality across the sites

from solstice import *


def read_file(path: str) -> str:
	with open(path, "r") as file:
		return file.read()


def read_file_sanitized(path: str) -> str:
	return (
		read_file(path)
		.replace("&", "&amp;")
		.replace(" ", "&nbsp;")
		.replace("<", "&lt;")
		.replace(">", "&gt;")
		.replace('"', "&quot;")
		.replace("'", "&apos;")
		.replace("\n", "<br>")
	)
