import argparse
import shutil
import sys

import solstice

from . import *


def run_cli():
	"""
	Runs the CLI. This should configure all the variables for the build then return if the build should proceed. Otherwise, this should exit the program.
	"""
	if _http_server is not None:
		# we're hot reloading, ignore this function call
		return

	parser = argparse.ArgumentParser("solstice", description="")
	parser.add_argument(
		"cmd", nargs="?", default="build", help='"build", "clean", or "serve"'
	)
	parser.add_argument("--release", action="store_true")
	parser.add_argument("-p", "--port", default=5123, type=int)

	args = parser.parse_args()
	solstice.cli_args = args

	match args.cmd:
		case "build":
			return
		case "clean":
			clean()
			sys.exit(0)
		case "serve":
			import threading

			clean()

			thread = threading.Thread(target=run_http_server, args=(args.port,))
			thread.start()

			try:
				hotreload()
			except KeyboardInterrupt:
				sys.stderr.write("\x1b[0J")  # clear from cursor down
				sys.stderr.flush()
				info("Shutting down cleanly...")
				assert _http_server
				_http_server.shutdown()
				thread.join()

			sys.exit(0)


def clean():
	try:
		with LogTimer(f"Cleaning {dist_path}"):
			shutil.rmtree(dist_path)
	except FileNotFoundError:
		warn("Nothing to clean.")


_http_server = None


def run_http_server(port):
	global _http_server
	try:
		from http.server import SimpleHTTPRequestHandler
		from socketserver import TCPServer

		class Handler(SimpleHTTPRequestHandler):
			protocol_version = "HTTP/1.1"

			def __init__(self, *args, **kwargs):
				super().__init__(*args, directory=dist_path, **kwargs)

			def log_message(self, format: str, *args):
				pass

			def send_head(self):
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

				# Call the superclass methods to actually serve the page.
				SimpleHTTPRequestHandler.do_GET(self)

			def end_headers(self):
				# do not remove these! firefox improperly caches resources and will break if it is not explicitly told to not cache anything
				self.send_header("Connection", "close")
				self.send_header(
					"Cache-Control", "no-cache, no-store, must-revalidate"
				)
				self.send_header("Pragma", "no-cache")
				self.send_header("Expires", "0")
				return super().end_headers()

		class ReuseAddrTCPServer(TCPServer):
			allow_reuse_address = True
			allow_reuse_port = True

			def __init__(self, *args, **kwargs):
				super().__init__(*args, **kwargs)

		with ReuseAddrTCPServer(("", port), Handler) as server:
			_http_server = server
			server.serve_forever()
	finally:
		_http_server = sys.exception()


def hotreload():
	import runpy
	import time
	import traceback
	from datetime import datetime

	from pygments import formatters, highlight, lexers
	from watchfiles import watch  # type: ignore (removes pyright hallucination)

	it = watch(module_path)

	# wait for server to start
	while not _http_server:
		time.sleep(0.1)
	if isinstance(_http_server, BaseException):
		return
	_addr, port = _http_server.server_address

	while True:
		sys.stderr.write("\x1b[2J\x1b[H")  # clear screen, reset cursor

		info(
			f"Watching module {pkgname} for changes. Visit website on http://localhost:{port}\n"
		)

		info(f"Starting build at {datetime.now()}")

		try:
			runpy.run_module(pkgname)
		except BaseException:
			tb_text = "".join(traceback.format_exc())

			lexer = lexers.get_lexer_by_name("pytb", stripall=True)
			formatter = formatters.TerminalFormatter()
			tb_colored = highlight(tb_text, lexer, formatter)

			print(tb_colored, file=sys.stderr)

		next(it)
