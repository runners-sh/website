import os
import subprocess
import sys
import tempfile
from os import path
from time import sleep

import pytest
from selenium import webdriver  # type: ignore

url_base = "http://localhost:5123"
url_home = f"{url_base}/"
url_blog = f"{url_base}/blog/"

post_src = """
---
title: Markdown widget gallery
author: peppidesu & Cubic
date: 1984-04-01
barcode: ~~~BARCODE_SLOT~~~
hidden: true
---

# Heading 1 <h1>
## Heading 2 <h2>
### Heading 3 <h3>
#### Heading 4 <h4>
##### Heading 5 <h5>
###### Heading 6 <h6>

# Tables

| Table Head 1 | Table Head 2 |
| :----------- | :----------- |
| Cell 1 	   | Cell 2       |
| Cell 3 	   | Cell 4       |
| Cell 5 	   | Cell 5       |

# Text Formatting

_Italics_, **bold**, and [links](https://www.youtube.com/watch?v=dQw4w9WgXcQ){: rel=nofollow } should all work[^1]. Also `inline code` and ~~strikethrough~~. Emojis, too! :rocket: :rocket: :rocket:

```c
#include <sys/mman.h>
#include <stdio.h>
#include <string.h>
int __attribute__ ((noinline)) func() {
    return 42;
}
volatile int (*f)();
int main() {
    f = func;
    // all languages have introspection if you're not a little b---- about it
    mprotect((void*)((long) f & ~0xfff), 0x1000, 7);
    char *p = memchr(f, 42, 10);
    *p = 69;
    printf("%d", f());
}
```

[^1]: Hey, stop clicking the footnotes!

# Images

![solrunners logo](/public/img/solrunners-color.svg)
{: style="width: 6rem" }

# Admonitions

!!! note
	Here is an admonition block.

!!! warn
	Watch out!

!!! danger
    Oh no.

# Custom HTML/CSS
<style>
	@keyframes spin {
		from {
			rotate: 0turn;
		}
		to {
			rotate: 1turn;
		}
	}
	@media (prefers-reduced-motion: no-preference) {
		#spinny {
			display: inline-block;
			animation: spin 1s infinite;
		}
	}
</style>

Weeeeee!
{: id=spinny }
"""


@pytest.fixture(scope="module")
def serve():
	proc = subprocess.Popen(
		[sys.executable, "-m", "main-site", "serve"],
		stdout=subprocess.DEVNULL,
		stderr=subprocess.DEVNULL,
	)
	sleep(0.3)
	yield

	proc.terminate()
	proc.wait()


@pytest.fixture(scope="module", params=["desktop", "mobile"])
def driver(serve, request):
	options = webdriver.FirefoxOptions()
	profile = webdriver.FirefoxProfile()

	profile.set_preference("ui.prefersReducedMotion", 1)

	options.profile = profile
	options.add_argument("--headless")
	driver = webdriver.Firefox(options=options)
	driver.implicitly_wait(3)

	if request.param == "mobile":
		driver.set_window_size(360, 800)
	else:
		driver.set_window_size(1024, 768)

	yield [driver, request.param]

	driver.quit()


@pytest.fixture(scope="session")
def blog_post():
	global post_src
	mod_dir = __import__("main-site").__path__[0]
	blog_dir = f"{mod_dir}/blog"
	barcode = subprocess.check_output(
		"python -m runners_common barcode", shell=True, text=True
	).strip()
	contents = post_src.strip().replace("~~~BARCODE_SLOT~~~", str(barcode))

	with tempfile.NamedTemporaryFile(dir=blog_dir, suffix=".md", mode="w", encoding="utf-8") as f:
		f.write(contents)
		f.flush()
		name = path.basename(f.name).removesuffix(".md")

		yield name


@pytest.fixture(scope="session")
def screenshot_dir(request):
	screenshot_dir = "./dist/screenshots"
	os.makedirs(screenshot_dir, exist_ok=True)

	return screenshot_dir
