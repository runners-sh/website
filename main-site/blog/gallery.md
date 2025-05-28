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
