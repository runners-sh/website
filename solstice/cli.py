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
	parser.add_argument("cmd", nargs="?", default="build", help='"build", "clean", or "serve"')
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

			def end_headers(self):
				self.send_header("Connection", "close")
				self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
				self.send_header("Pragma", "no-cache")
				self.send_header("Expires", "0")
				return super().end_headers()

		with TCPServer(("", port), Handler) as server:
			_http_server = server
			server.serve_forever()
	finally:
		_http_server = sys.exception()


def hotreload():
	import runpy
	import time
	from datetime import datetime

	from watchfiles import watch  # type: ignore (removes pyright hallucination)

	it = watch(module_path)
	is_first = True

	# wait for server to start
	while not _http_server:
		time.sleep(0.1)
	if isinstance(_http_server, BaseException):
		return
	_addr, port = _http_server.server_address

	sys.stderr.write("\x1b[2J\x1b[1;1H")  # clear screen, reset cursor
	sys.stderr.flush()

	info(f"Watching module {pkgname} for changes. Visit website on http://localhost:{port}")

	while True:
		sys.stderr.write("\x1b[2;1H")  # move cursor to (0, 1)
		sys.stderr.flush()

		if is_first:
			# we don't want to wait for a file change so just give the first build a free pass
			is_first = False
		else:
			next(it)

		sys.stderr.write("\x1b[0J\x1b[B")  # clear from cursor down, move cursor down
		sys.stderr.flush()
		info(f"Starting build at {datetime.now()}")

		runpy.run_module(pkgname)
