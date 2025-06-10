# pyright: reportMissingImports=false, reportMissingModuleSource=false
import os
import shutil
from os import path
from typing import Any, Literal

import frontmatter
import jinja2
import markdown
from l2m4m import LaTeX2MathMLExtension
from pymdownx.emoji import EmojiExtension
from pymdownx.emoji import to_alt as emoji_to_alt
from pymdownx.highlight import HighlightExtension

from .log import LogTimer, warn

__all__ = [
	"filename_to_html",
	"read_file",
	"recurse_files",
	"SiteGenerator",
	"Page",
	"MarkdownPage",
]


def filename_to_html(name: str) -> str:
	"""Changes the given filename extension to .html, regardless of what it is."""
	return path.splitext(name)[0] + ".html"


def read_file(path: str) -> str:
	"""Reads a file and returns its contents. A bit of a dumb wrapper if you ask me, but... oh well."""
	with open(path, "r") as file:
		return file.read()


def recurse_files(root: str, extensions: list[str]):
	"""
	Recursively find files in a directory with specified extensions.

	# Arguments
	- `root`: The root directory to start searching from.
	- `extensions`: A list of file extensions to filter by (e.g., ['.md', '.txt']).

	# Yields
	Tuples of (directory name, file name, file base name, extension) for each matching file.
	"""
	for dirname, dirs, files in os.walk(root):
		for file in files:
			name, ext = path.splitext(file)
			if ext not in extensions:
				continue
			yield (dirname, file, name, ext)


class SiteGenerator:
	"""
	`SiteGenerator` contains the context and functionality needed to generate your site.

	# Example

	```python
	import solstice
	ssg = solstice.SiteGenerator()
	ssg.page("index.jinja", title="Hello world!")
	ssg.copy("public")
	```
	"""

	project_dir: str
	""" Path to the project directory """

	output_path: str
	""" Output directory for the site generator """

	templates_path: str
	""" Path to load the Jinja2 templates from """

	profile: Literal["dev", "prod"]
	""" Release profile. Can be 'dev' (development) or 'prod' (production) """

	jinja_env: jinja2.Environment
	""" Jinja2 environment data """

	original_cwd: str
	""" The original working directory of the process when launched. """

	extra_watches: list[str]
	""" Files/directories to watch in addition to the main project directory."""

	_md_instance: markdown.Markdown

	def __init__(
		self,
		project_dir: str | None = None,
		output_path: str | None = None,
		templates_path: str | None = None,
		extra_watches: list[str] | None = None,
		profile: Literal["dev", "prod"] = "dev",
	):
		if project_dir is None:
			import inspect

			# python magic to get the path of the caller
			prev_frame = inspect.stack()[1]
			project_dir = path.dirname(path.abspath(prev_frame.filename))

		self.project_dir = project_dir
		self.original_cwd = os.getcwd()
		os.chdir(self.project_dir)

		self.output_path = output_path or "dist"

		self.templates_path = templates_path or "templates"

		self.extra_watches = extra_watches or []
		self.profile = profile

		self.jinja_env = jinja2.Environment(
			loader=jinja2.FileSystemLoader(self.templates_path),
			autoescape=True,
			optimized=(self.profile == "prod"),
		)
		self.jinja_env.globals["profile"] = self.profile

		self._md_instance = markdown.Markdown(
			extensions=[
				"admonition",
				"pymdownx.extra",
				"pymdownx.tilde",
				"toc",
				EmojiExtension(emoji_generator=emoji_to_alt),
				HighlightExtension(
					css_class="codehilite",
					linenums=True,
				),
				LaTeX2MathMLExtension(),
			],
		)

	def output_path_for(self, name: str) -> str:
		"""
		Get the full output path for the given path, and create directories if they don't exist yet.
		"""
		p = path.join(self.output_path, name)
		dirname = path.dirname(p)
		os.makedirs(dirname, exist_ok=True)
		return p

	def render(self, name: str, **kwargs) -> str:
		"""Render a template with the given values."""
		return self.jinja_env.get_template(name).render(kwargs)

	def md_to_html(self, markdown: str) -> tuple[str, str]:
		"""
		Convert markdown to HTML, and generate a table of contents if applicable.
		# Arguments
		- `markdown`: The markdown content to convert.

		# Returns
		A tuple containing the HTML content and the table of contents (if any).
		"""
		self._md_instance.reset()
		content = self._md_instance.convert(markdown)
		return content, self._md_instance.toc  # type: ignore

	def load_md(self, path: str) -> tuple[str, str, dict[str, Any]]:
		"""
		Load a markdown file, parse its frontmatter, and convert the remaining source to HTML.
		# Arguments
		- `path`: The path to the markdown file.

		# Returns
		A tuple containing the HTML content, table of contents, and frontmatter metadata.
		"""
		with open(path, "r") as f:
			meta, content = frontmatter.parse(f.read())
			content, toc = self.md_to_html(content)
			return content, toc, meta

	def copy(self, dir: str):
		"""
		Copy a directory to the output path, without altering its contents.
		Used for copying static assets like images, CSS, etc.

		# Arguments
		- `dir`: The directory to copy.
		"""
		if path.exists(dir):
			dist = self.output_path_for(dir)
			with LogTimer(f"Copying directory '{dir}'..."):
				shutil.copytree(dir, dist, dirs_exist_ok=True)

	def clean(self):
		"""Clean the output directory, removing it and all its contents."""
		try:
			with LogTimer(f"Cleaning {self.output_path}"):
				shutil.rmtree(self.output_path)
		except FileNotFoundError:
			warn("Nothing to clean.")

	def page(self, template_name: str, output_path: str | None = None, **kwargs):
		"""
		Generate a page using the specified template and optionally an output path.
		# Arguments
		- `template_name`: The name of the Jinja2 template to use.
		- `output_path`: The path to save the generated page. If None, it will be derived from the template name.
		- `**kwargs`: Additional parameters to pass to the template.

		# Example
		```python
		import solstice
		ssg = solstice.SiteGenerator()
		ssg.page("home.jinja", output_path="index.html", title="Hello world!")
		```
		"""
		with Page(self, template_name, output_path) as pg:
			pg.set_params(**kwargs)

	def markdown_page(
		self,
		template_name: str,
		content_path: str,
		output_path: str | None = None,
		**kwargs,
	):
		"""
		Generate a markdown page using the specified template and content file.
		# Arguments
		- `template_name`: The name of the Jinja2 template to use.
		- `content_path`: The path to the markdown content file.
		- `output_path`: The path to save the generated page. If None, it will be derived from the content path.
		- `**kwargs`: Additional parameters to pass to the template.

		# Example
		```python
		import solstice
		ssg = solstice.SiteGenerator()
		ssg.markdown_page("blog.jinja", "posts/my_post.md", output_path="blog/my_post.html")
		```
		"""
		with MarkdownPage(self, template_name, content_path, output_path) as pg:
			pg.set_params(**kwargs)


class Page:
	"""
	Context manager for generating a page using a Jinja2 template.
	This class is mostly used as a base class to derive other page types from, such as `MarkdownPage`, but can also be used directly (as is done in the implementation of `page()`).

	# Example
	```python
	import solstice

	ssg = solstice.SiteGenerator()
	with solstice.Page(ssg, "index.jinja") as page:
		page.set_params(title="Hello world!")

	# The page will be built automatically when exiting the context.
	```
	"""

	def __init__(
		self,
		gen: SiteGenerator,
		template_name: str,
		output_path: str | None = None,
	):
		self.template_name = template_name
		self.output_path = output_path or filename_to_html(self.template_name)
		self.gen = gen

		self._log_timer = LogTimer(
			f"Building '{template_name}' -> '{self.output_path}'...",
			f"Built '{self.output_path}' in {{}}",
		)
		self.params = {}

	def set_params(self, **params):
		"""
		Set parameters for the page. If a key is already set, a warning is shown and the value gets overwritten.

		# Arguments
		- `**params`: The parameters to set for the page. Each key-value pair will be made available in the template.

		# Example
		```python
		import solstice
		ssg = solstice.SiteGenerator()
		with solstice.Page(ssg, "index.jinja") as page:
			page.set_params(
				title="Hello world!",
				description="This is my homepage.",
				blog_posts=["Post 1", "Post 2"]
			)
		```
		"""
		self._set_params_internal(
			"key '{}' is set multiple times.",
			params,
		)

	def _set_params_internal(
		self,
		dup_warn: str,
		params: dict[str, Any],
		overwrite=True,
	):
		"""
		Internal method to set parameters for the page. Allows customization of the warning message for duplicate keys.
		# Arguments
		- `dup_warn`: The warning message to show when a key is set multiple times.
		- `overwrite`: If `True`, overwrite existing keys; otherwise, keep the existing value.
		- `**params`: The parameters to set for the page.
		"""
		for key, val in params.items():
			if key in self.params.keys():
				warn(dup_warn.format(key))
				if overwrite:
					self.params[key] = val
			else:
				self.params[key] = val

	def __enter__(self):
		self._log_timer.__enter__()
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.build()
		self._log_timer.__exit__(exc_type, exc_value, traceback)

	def build(self):
		"""
		Build the page by rendering the template with the provided parameters and saving it to the output path.
		Called automatically when exiting the context manager.
		"""
		dest = self.gen.output_path_for(self.output_path)
		with open(dest, "w") as file:
			contents = self.gen.render(self.template_name, **self.params)
			file.write(contents)


class MarkdownPage(Page):
	"""
	Context manager for generating a page from a markdown file using a Jinja2 template.

	This class extends `Page` to handle markdown content, converting it to HTML and extracting frontmatter metadata.

	# Example
	```python
	import solstice

	ssg = solstice.SiteGenerator()
	with solstice.MarkdownPage(
		ssg,
		"blog.jinja",
		content_path="posts/my_post.md",
		output_path="blog/my_post.html"
	) as page:
		page.set_params(title="My Post", author="John Doe")

	# The page will be built automatically when exiting the context.
	```

	# Notes
	- The parameters set using `set_params()` will overwrite any frontmatter keys in the markdown file.
	- The `content` and `toc` parameters are reserved for the markdown content and table of contents, respectively, and will be set automatically.
	"""

	def __init__(
		self,
		gen: SiteGenerator,
		template_name: str,
		content_path: str,
		output_path: str | None = None,
	):
		super().__init__(gen, template_name, output_path)
		self._log_timer = LogTimer(
			f"Building '{content_path}' -> '{output_path}'...",
			f"Built '{self.output_path}' in {{}}",
		)
		self.content_path = content_path
		self.content, self.toc, self.meta = self.gen.load_md(self.content_path)

	def build(self):
		self._set_params_internal(
			"frontmatter: key '{}' is already set by the caller, skipping...",
			self.meta,
			overwrite=False,
		)
		self._set_params_internal(
			"key '{}' is reserved for markdown content.",
			{
				"content": self.content,
				"toc": self.toc,
			},
		)

		return super().build()
