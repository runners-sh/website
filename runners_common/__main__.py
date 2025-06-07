import argparse
import sys

import solstice.log as log

from . import funbar

parser = argparse.ArgumentParser("solstice", description="")
subparsers = parser.add_subparsers(
	title="subcommands", description="valid subcommands:", required=True, dest="cmd"
)

barcode_parser = subparsers.add_parser("barcode", help="Generate a random barcode or a custom one")
barcode_parser.add_argument(
	"code",
	nargs="?",
	help="A 7-digit number to generate a custom barcode, or nothing to generate a random one",
)

args = parser.parse_args()

match args.cmd:
	case "barcode":
		if args.code is not None and len(args.code) == 7:
			code = "".join(map(str, funbar.barcode_to_digits(args.code[0], num_digits=7)))
		else:
			if args.code is not None:
				log.warn(
					"argument given to barcode command should either be nonexistent for a random barcode or a number of length 7 to generate a custom one"
				)
			code = funbar.generate_rcn_barcode("./dist/main-site")  # [TODO]: yikes
		print(f"{code:08}")
		sys.exit(0)
