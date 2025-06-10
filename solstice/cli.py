import argparse
import importlib
import os
import sys
from enum import Enum
from typing import Any

from .log import info, warn
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


# hot reloading requires build_func to be replaced so we can't use e.g. a function parameter to communicate it
build_func: Any = None


def entrypoint(ssg: SiteGenerator, extra_watches: list[str] | None = None):
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
		global build_func
		# the hot reloading code calls importlib.reload which will rerun the entrypoint function; in that case we should just replace the function and not continue with the rest of the cli
		if _http_server:
			build_func = func
			return

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

				build_func = func
				try:
					hotreload(ssg, extra_watches=extra_watches or [])
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
# if the http server thread crashes, this will be set to the exception so the other threads can gracefully fail
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


def hotreload(ssg: SiteGenerator, extra_watches: list[str]):
	import time
	import traceback
	from datetime import datetime

	import pygments
	import pygments.formatters
	import pygments.lexers
	import watchfiles  # type: ignore (removes pyright hallucination)

	it = watchfiles.watch(ssg.project_dir, *map(os.path.realpath, extra_watches))

	# wait for server to start
	while True:
		time.sleep(0.1)
		if _http_server:  # Server started
			break
		if _http_server_exception:  # Server crashed
			return

	_addr, port = _http_server.server_address

	class ReloadType(Enum):
		# no python should be reloaded, just run the function again
		SOFT = 0
		# the project python module should be reloaded
		PROJECT = 1
		# everything should be reloaded. this is used when `extra_watches` is passed to the ssg and a library is modified; solstice doesn't do advanced dependency tree detection shenanigans so we be conservative and reload the whole thing
		FULL = 2

		def __lt__(self, other):
			return self.value < other.value

	reload_type = ReloadType.SOFT

	while True:
		sys.stderr.write("\x1b[2J\x1b[H")  # clear screen, reset cursor

		info(f"Watching for changes. Visit website on http://localhost:{port}\n")

		info(f"Starting build at {datetime.now()}")

		if reload_type == ReloadType.PROJECT:
			# find the module that corresponds to the project directory
			try:
				module = next(
					module
					for module in sys.modules.values()
					if hasattr(module, "__path__")
					and module.__path__[0].startswith(ssg.project_dir)
				)

				importlib.reload(module)

				# now do a soft reload. this is technically redundant due to the code below but y'know, readability
				reload_type = ReloadType.SOFT
			except StopIteration:
				warn("can't find the module, doing a full reload instead")
				reload_type = ReloadType.FULL
		if reload_type == ReloadType.FULL:
			# incredibly cursed hack to get the actual argv of the process: https://stackoverflow.com/a/57914236
			# sys.argv doesn't work as it doesn't consider command-line switches (e.g. -m)
			import ctypes

			argc = ctypes.c_int()
			argv = ctypes.POINTER(ctypes.c_wchar_p)()
			ctypes.pythonapi.Py_GetArgcArgv(ctypes.byref(argc), ctypes.byref(argv))

			os.chdir(ssg.original_cwd)
			os.execv(sys.executable, [argv[i] for i in range(argc.value)])
			raise Exception("unreachable; see execv call")

		# reload_type == ReloadType.SOFT
		try:
			build_func()
		except BaseException:
			# catch all exceptions to prevent hot-reload breakage and output them to stderr
			tb_text = "".join(traceback.format_exc())
			lexer = pygments.lexers.get_lexer_by_name("pytb", stripall=True)
			formatter = pygments.formatters.TerminalFormatter()
			tb_colored = pygments.highlight(tb_text, lexer, formatter)

			print(tb_colored, file=sys.stderr)

		# wait for next change
		item = next(it)

		reload_type = ReloadType.SOFT
		for _change_type, changed_path in item:
			if changed_path.endswith(".py"):
				if changed_path.startswith(ssg.project_dir):
					reload_type = max(reload_type, ReloadType.PROJECT)
				else:
					reload_type = max(reload_type, ReloadType.FULL)
