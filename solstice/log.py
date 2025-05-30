# custom logging implementation bcuz the built-in one kinda sucks
import sys
import time
from enum import Enum

__all__ = [
	"LogLevel",
	"LogTimer",
	"log",
	"debug",
	"info",
	"success",
	"warn",
	"error",
]


class LogLevel(Enum):
	DEBUG = 0
	INFO = 10
	SUCCESS = 15
	WARN = 20
	ERROR = 30


ANSI_COLORS = {
	LogLevel.DEBUG: "\x1b[2m",
	LogLevel.INFO: "\x1b[36m",
	LogLevel.SUCCESS: "\x1b[32m",
	LogLevel.WARN: "\x1b[33m",
	LogLevel.ERROR: "\x1b[31m",
}


def log(level: LogLevel, msg: str):
	# the standard string padding functions don't work as they don't take into account ANSI codes
	print(
		f"[{ANSI_COLORS[level]}{level.name}\x1b[0m]" + " " * (8 - len(level.name)) + msg,
		file=sys.stderr,
	)


def debug(msg: str):
	log(LogLevel.DEBUG, msg)


def info(msg: str):
	log(LogLevel.INFO, msg)


def success(msg: str):
	log(LogLevel.SUCCESS, msg)


def warn(msg: str):
	log(LogLevel.WARN, msg)


def error(msg: str):
	log(LogLevel.ERROR, msg)


class LogTimer:
	def __init__(self, initial_msg: str, ending_msg: str = "Completed in {}"):
		self.initial_msg = initial_msg
		self.ending_msg = ending_msg

	def __enter__(self):
		info(self.initial_msg)
		self.start_time = time.time()

	def __exit__(self, exc_type, exc_value, traceback):
		if exc_value or hasattr(sys, "last_exc"):
			return
		elapsed = time.time() - self.start_time
		time_str = f"{elapsed:.02f}s" if elapsed >= 1 else f"{elapsed * 1000:.0f}ms"
		success(self.ending_msg.format(time_str))
		del self.start_time
