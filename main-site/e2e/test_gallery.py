import subprocess
import sys
import tempfile
from os import path
from time import sleep

import pytest
from selenium import webdriver  # type: ignore
from selenium.webdriver.common.by import By  # type: ignore

url_base = "http://localhost:5123"

post_src = """
---
title: Markdown widget gallery
author: peppidesu & Cubic
date: 1984-04-01
barcode: 45322761
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


@pytest.fixture
def environment():
	mod_dir = __import__("main-site").__path__[0]
	blog_dir = f"{mod_dir}/blog"
	with tempfile.NamedTemporaryFile(dir=blog_dir, suffix=".md", mode="w", encoding="utf-8") as f:
		f.write(post_src.strip())
		f.flush()
		name = path.basename(f.name).removesuffix(".md")

		proc = subprocess.Popen(
			[sys.executable, "-m", "main-site", "serve"],
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL,
		)
		sleep(0.5)

		options = webdriver.FirefoxOptions()
		profile = webdriver.FirefoxProfile()
		profile.set_preference("ui.prefersReducedMotion", 1)
		options.profile = profile
		options.add_argument("--headless")
		driver = webdriver.Firefox(options=options)
		driver.implicitly_wait(5)

		yield driver, f"{url_base}/blog/{name}"

		proc.kill()
		driver.quit()



def test_toc_heading_link_layers(environment):
	driver, gallery_url = environment
	driver.get(gallery_url)

	table_of_contents = driver.find_element(
		By.XPATH,
		""".//main//aside//div[contains(concat(" ",normalize-space(@class)," ")," toc ")]""",
	)

	header_link = table_of_contents.find_element(By.LINK_TEXT, "Heading 1")
	header_link.click()
	assert driver.current_url == f"{gallery_url}#heading-1"

	header_link = table_of_contents.find_element(By.LINK_TEXT, "Heading 2")
	header_link.click()
	assert driver.current_url == f"{gallery_url}#heading-2"

	header_link = table_of_contents.find_element(By.LINK_TEXT, "Heading 3")
	header_link.click()
	assert driver.current_url == f"{gallery_url}#heading-3"

	header_link = table_of_contents.find_element(By.LINK_TEXT, "Heading 4")
	header_link.click()
	assert driver.current_url == f"{gallery_url}#heading-4"

	header_link = table_of_contents.find_element(By.LINK_TEXT, "Heading 5")
	header_link.click()
	assert driver.current_url == f"{gallery_url}#heading-5"

	header_link = table_of_contents.find_element(By.LINK_TEXT, "Heading 6")
	header_link.click()
	assert driver.current_url == f"{gallery_url}#heading-6"


def test_italics(environment):
	driver, gallery_url = environment
	driver.get(gallery_url)

	article = driver.find_element(By.TAG_NAME, "article")
	element = article.find_element(By.XPATH, ".//em")
	assert element.text == "Italics"


def test_bold(environment):
	driver, gallery_url = environment
	driver.get(gallery_url)

	article = driver.find_element(By.TAG_NAME, "article")
	element = article.find_element(By.XPATH, ".//strong")
	assert element.text == "bold"


def test_links(environment):
	driver, gallery_url = environment
	driver.get(gallery_url)
	article = driver.find_element(By.TAG_NAME, "article")
	element = article.find_element(By.LINK_TEXT, "links")
	element.click()
	assert driver.current_url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def test_inline_code(environment):
	driver, gallery_url = environment
	driver.get(gallery_url)

	article = driver.find_element(By.TAG_NAME, "article")
	element = article.find_element(By.XPATH, ".//code")
	assert element.text == "inline code"


def test_strikethrough(environment):
	driver, gallery_url = environment
	driver.get(gallery_url)

	article = driver.find_element(By.TAG_NAME, "article")
	element = article.find_element(By.XPATH, ".//del")
	assert element.text == "strikethrough"
