from conftest import (
	url_blog_gallery,
	url_blog_headers,
	url_member_bob,
	url_member_johndoe,
)
from selenium.webdriver.common.by import By  # type: ignore


def test_member_social_links(driver):
	driver.get(url_member_johndoe)

	links_par = driver.find_element(By.CSS_SELECTOR, ".links")
	links: list = links_par.find_elements(By.TAG_NAME, "a")

	assert len(links) == 3


def test_member_post_link(driver):
	driver.get(url_member_johndoe)

	postlist = driver.find_element(By.CSS_SELECTOR, ".post-list")
	links = postlist.find_elements(By.TAG_NAME, "a")

	assert len(links) == 2
	urls = [x.get_attribute("href") for x in links]

	assert url_blog_gallery in urls
	assert url_blog_headers in urls


def test_member_post_list_empty(driver):
	driver.get(url_member_bob)

	postlist = driver.find_element(By.CSS_SELECTOR, ".post-list")
	links = postlist.find_elements(By.TAG_NAME, "a")

	assert len(links) == 0
