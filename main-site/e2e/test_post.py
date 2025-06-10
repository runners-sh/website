from os import path

from conftest import url_blog, url_member
from selenium.webdriver.common.by import By  # type: ignore


def test_author_links(blog_post, driver):
	gallery_url = path.join(url_blog, blog_post)
	driver.get(gallery_url)

def test_toc_heading_link_layers(blog_post, driver):
	gallery_url = path.join(url_blog, blog_post)
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


def test_italics(blog_post, driver):
	gallery_url = path.join(url_blog, blog_post)
	driver.get(gallery_url)

	article = driver.find_element(By.TAG_NAME, "article")
	element = article.find_element(By.XPATH, ".//em")
	assert element.text == "Italics"


def test_bold(blog_post, driver):
	gallery_url = path.join(url_blog, blog_post)
	driver.get(gallery_url)

	article = driver.find_element(By.TAG_NAME, "article")
	element = article.find_element(By.XPATH, ".//strong")
	assert element.text == "bold"


def test_links(blog_post, driver):
	gallery_url = path.join(url_blog, blog_post)
	driver.get(gallery_url)

	article = driver.find_element(By.TAG_NAME, "article")
	element = article.find_element(By.LINK_TEXT, "links")
	assert element.get_attribute("href") == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def test_inline_code(blog_post, driver):
	gallery_url = path.join(url_blog, blog_post)
	driver.get(gallery_url)

	article = driver.find_element(By.TAG_NAME, "article")
	element = article.find_element(By.XPATH, ".//code")
	assert element.text == "inline code"


def test_strikethrough(blog_post, driver):
	gallery_url = path.join(url_blog, blog_post)
	driver.get(gallery_url)

	article = driver.find_element(By.TAG_NAME, "article")
	element = article.find_element(By.XPATH, ".//del")
	assert element.text == "strikethrough"

def test_author_link(blog_post, member_page, driver):
	gallery_url = path.join(url_blog, blog_post)
	driver.get(gallery_url)

	meta = driver.find_element(By.CLASS_NAME, "meta")
	link = meta.find_element(By.TAG_NAME, "a")
	link.click()
	assert driver.current_url == path.join(url_member, member_page)
