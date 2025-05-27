"""
The Fun Bar Signature (or "fun bar" for short) is an EAN-8 barcode[^1] falling in the Restricted Circulation Numbers (aka private use) range. This is to make sure someone scanning a Fun Bar Signature with their phone won't turn up a package of frozen peas or whatever.

The choice of EAN-8 is because it's horizontal, it fits in the narrow height of the Fun Bar Signature, is decently short, and it has wide compatibility with phone scanners.

[1]: https://ref.gs1.org/standards/genspecs/, 1.4.5 for RCN range, 5.2.1 for the EAN-8 specification
"""

# A = NUMBER_SETS[digit]
# B = NUMBER_SETS[digit][::-1]
# C = NUMBER_SETS[digit] # but C has the dark bars first
NUMBER_SETS = [
	[3, 2, 1, 1],
	[2, 2, 2, 1],
	[2, 1, 2, 2],
	[1, 4, 1, 1],
	[1, 1, 3, 2],
	[1, 2, 3, 1],
	[1, 1, 1, 4],
	[1, 3, 1, 2],
	[1, 2, 1, 3],
	[3, 1, 1, 2],
]

assert all(sum(widths) == 7 for widths in NUMBER_SETS)

NORMAL_GUARD_BAR = [1, 1, 1]
CENTER_GUARD_BAR = [1, 1, 1, 1, 1]


def bar_widths_from_ean8(s: int | str, invert=False, padding=6) -> list[int]:
	s = str(s)
	assert type(s) is str and len(s) == 7 and all(c in "0123456789" for c in s)
	digits = [*map(int, s)]

	# get check digit
	check_digit = -sum(digit * (3, 1)[i % 2] for i, digit in enumerate(digits)) % 10
	digits.append(check_digit)

	barcode = []
	if invert:
		barcode.append(0)  # flip the first bar
	if padding > 0:
		barcode.append(padding)
	barcode += NORMAL_GUARD_BAR
	for c in digits[:4]:
		barcode += NUMBER_SETS[c]
	barcode += CENTER_GUARD_BAR
	for c in digits[4:]:
		barcode += NUMBER_SETS[c]
	barcode += NORMAL_GUARD_BAR
	if padding > 0:
		barcode.append(padding)

	return barcode


# A unique "pepper" to prefix seeds with when hashing. Make sure this is secure!
SOLSTICE_PEPPER = b"\x97\xf2k\x82v\xbf8\xf7\x01\x123\x9a^\xfb&d"


def generate_rcn_number(seed: str | bytes | None) -> int:
	"""
	Hashes a string into an RCN (private use) number.
	"""
	import hashlib

	if str is None:
		from . import warn

		warn("seed is None, using dummy RCN")
		return 69

	if type(seed) is str:
		seed = seed.encode()
	assert type(seed) is bytes  # bc pyright is kind of an idiot

	hash = hashlib.shake_128(SOLSTICE_PEPPER + seed, usedforsecurity=False)
	integer = int.from_bytes(hash.digest(128 // 8))

	# only 2 and 4 are valid RCN starting digits so just check a random bit to decide
	first_digit = (2, 4)[integer >> 127]

	return first_digit * 1000000 + integer % 1000000


def html_from_bar_widths(
	bar_widths: list[int],
	colors: list[str] = ["fg", "a1", "a2", "a3"],
	width_prefix: str = "w",
	element_name: str = "b",
) -> str:
	from random import Random

	rand = Random()
	rand.seed(bytes(bar_widths))
	return "".join(
		f'<{element_name} class="{width_prefix}{bar_width} {rand.choice(colors) if i % 2 == 0 else ""}"></{element_name}>'
		for i, bar_width in enumerate(bar_widths)
	)


def funbar_html_from_seed(seed: str | bytes) -> str:
	return html_from_bar_widths(bar_widths_from_ean8(generate_rcn_number(seed)))
