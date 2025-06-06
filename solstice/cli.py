import argparse
import os
import sys
from typing import Callable

from .log import info
from .sitegen import SiteGenerator


def parse_cli():
	"""
	Parse arguments from the CLI.
	"""
	parser = argparse.ArgumentParser("solstice", description="")
	parser.add_argument("cmd", nargs="?", default="build", help='"build", "clean", or "serve"')
	parser.add_argument("--release", action="store_true")
	parser.add_argument("-p", "--port", default=5123, type=int)

	args = parser.parse_args()

	return args


def entrypoint(ssg: SiteGenerator):
	"""
	`@cli.entrypoint` is used to mark the function that builds your site. It will wrap this function
	into the CLI, calling it when building/hot-reloading.

	# Example
	```python
	import solstice
	from solstice import cli

	ssg = solstice.SiteGenerator(__package__)

	@cli.entrypoint(ssg)
	def build():
	    ssg.page("index.jinja", title="Hello world!")
	    ssg.copy("public")
	```
	"""

	def inner(func):
		args = parse_cli()
		match args.cmd:
			case "build":  # Build the website
				func()
			case "clean":  # Clean output dir
				ssg.clean()
			case "serve":  # Serve with hot-reloading
				import threading

				ssg.clean()

				thread = threading.Thread(target=run_http_server, args=(args.port, ssg.output_path))
				thread.start()

				try:
					hotreload(ssg, func)
				except KeyboardInterrupt:  # Ctrl+C, finalize
					sys.stderr.write("\x1b[0J")  # clear from cursor down
					sys.stderr.flush()
					info("Shutting down cleanly...")
					assert _http_server
					_http_server.shutdown()
					thread.join()
		return func

	return inner


_http_server = None
_http_server_exception = None


def run_http_server(port, dir):
	"""
	Background process that serves the content at `dir`
	"""
	global _http_server
	try:
		from http.server import SimpleHTTPRequestHandler
		from socketserver import TCPServer

		class Handler(SimpleHTTPRequestHandler):
			protocol_version = "HTTP/1.1"

			def __init__(self, *args, **kwargs):
				super().__init__(*args, directory=dir, **kwargs)

			def log_message(self, format: str, *args):  # discard log messages
				pass

			def send_head(self):
				# Do not remove!
				# Firefox doesn't play well with Python's HTTP server caching, therefore we disable caching altogether.
				# This is not a big deal as this server is only for development anyway.
				if "If-Modified-Since" in self.headers:
					del self.headers["If-Modified-Since"]
				if "If-None-Match" in self.headers:
					del self.headers["If-None-Match"]
				return super().send_head()

			# from https://stackoverflow.com/questions/28419287/configuring-simplehttpserver-to-assume-html-for-suffixless-urls
			def do_GET(self):
				path = self.translate_path(self.path)

				# If the path doesn't exist, assume it's a resource suffixed '.html'.
				if not os.path.exists(path):
					self.path = self.path + ".html"

				super().do_GET()

			def end_headers(self):
				# Do not remove!
				# Firefox also needs to be explicitly told to not cache anything with the following headers.
				self.send_header("Connection", "close")
				self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
				self.send_header("Pragma", "no-cache")
				self.send_header("Expires", "0")
				return super().end_headers()

		class ReuseAddrTCPServer(TCPServer):
			# Workaround that prevents the server from sometimes being unable to bind to the address, even if no process is currently bound to it.
			allow_reuse_address = True
			allow_reuse_port = True

			def __init__(self, *args, **kwargs):
				super().__init__(*args, **kwargs)

		with ReuseAddrTCPServer(("", port), Handler) as server:
			_http_server = server
			server.serve_forever()
	finally:
		_http_server_exception = sys.exception()


def hotreload(ssg: SiteGenerator, build_func: Callable):
	import time
	import traceback
	from datetime import datetime

	from pygments import formatters, highlight, lexers
	from watchfiles import watch  # type: ignore (removes pyright hallucination)

	it = watch(ssg.project_dir)  # file watcher

	# wait for server to start
	while True:
		time.sleep(0.1)
		if _http_server:  # Server started
			break
		if _http_server_exception:  # Server crashed
			return

	_addr, port = _http_server.server_address

	while True:
		sys.stderr.write("\x1b[2J\x1b[H")  # clear screen, reset cursor

		info(
			f"Watching path {ssg.project_dir} for changes. Visit website on http://localhost:{port}\n"
		)

		info(f"Starting build at {datetime.now()}")

		try:
			build_func()
		except BaseException:
			# catch all exceptions to prevent hot-reload breakage, and output them in a similar fashion to stderr.
			tb_text = "".join(traceback.format_exc())
			lexer = lexers.get_lexer_by_name("pytb", stripall=True)
			formatter = formatters.TerminalFormatter()
			tb_colored = highlight(tb_text, lexer, formatter)

			print(tb_colored, file=sys.stderr)

		next(it)  # wait for file changes
