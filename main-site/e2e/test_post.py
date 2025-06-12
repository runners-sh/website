from conftest import url_blog_gallery, url_member_johndoe
from selenium.webdriver.common.by import By  # type: ignore


def test_toc_heading_link_layers(driver):
	driver.get(url_blog_gallery)

	table_of_contents = driver.find_element(
		By.XPATH,
		""".//main//aside//div[contains(concat(" ",normalize-space(@class)," ")," toc ")]""",
	)

	header_link = table_of_contents.find_element(By.LINK_TEXT, "Heading 1")
	header_link.click()
	assert driver.current_url == f"{url_blog_gallery}#heading-1"

	header_link = table_of_contents.find_element(By.LINK_TEXT, "Heading 2")
	header_link.click()
	assert driver.current_url == f"{url_blog_gallery}#heading-2"

	header_link = table_of_contents.find_element(By.LINK_TEXT, "Heading 3")
	header_link.click()
	assert driver.current_url == f"{url_blog_gallery}#heading-3"

	header_link = table_of_contents.find_element(By.LINK_TEXT, "Heading 4")
	header_link.click()
	assert driver.current_url == f"{url_blog_gallery}#heading-4"

	header_link = table_of_contents.find_element(By.LINK_TEXT, "Heading 5")
	header_link.click()
	assert driver.current_url == f"{url_blog_gallery}#heading-5"

	header_link = table_of_contents.find_element(By.LINK_TEXT, "Heading 6")
	header_link.click()
	assert driver.current_url == f"{url_blog_gallery}#heading-6"


def test_italics(driver):
	driver.get(url_blog_gallery)

	article = driver.find_element(By.TAG_NAME, "article")
	element = article.find_element(By.XPATH, ".//em")
	assert element.text == "Italics"


def test_bold(driver):
	driver.get(url_blog_gallery)

	article = driver.find_element(By.TAG_NAME, "article")
	element = article.find_element(By.XPATH, ".//strong")
	assert element.text == "bold"


def test_links(driver):
	driver.get(url_blog_gallery)

	article = driver.find_element(By.TAG_NAME, "article")
	element = article.find_element(By.LINK_TEXT, "links")
	assert element.get_attribute("href") == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def test_inline_code(driver):
	driver.get(url_blog_gallery)

	article = driver.find_element(By.TAG_NAME, "article")
	element = article.find_element(By.XPATH, ".//code")
	assert element.text == "inline code"


def test_strikethrough(driver):
	driver.get(url_blog_gallery)

	article = driver.find_element(By.TAG_NAME, "article")
	element = article.find_element(By.XPATH, ".//del")
	assert element.text == "strikethrough"


def test_author_link(driver):
	driver.get(url_blog_gallery)

	meta = driver.find_element(By.CLASS_NAME, "meta")
	link = meta.find_element(By.TAG_NAME, "a")
	link.click()
	assert driver.current_url == url_member_johndoe
