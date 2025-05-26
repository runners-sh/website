from tempfile import NamedTemporaryFile

from . import *


def test_load_markdown():
	with NamedTemporaryFile(mode="w", suffix=".md") as f:
		f.write(
			"""
---
title: "Hello, World!"
---
# Hello, world!
        """.strip()
		)
		f.flush()

		meta, content = load_markdown(f.name)

		assert meta == {"title": "Hello, World!"}
		assert content == '<h1 id="hello-world">Hello, world!</h1>'
