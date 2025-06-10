from os import path

from conftest import url_blog
from selenium.webdriver.common.by import By  # type: ignore


def test_post_list(blog_post, driver):
	driver.get(url_blog)
	postlist = driver.find_element(By.CSS_SELECTOR, ".post-list")
	links = postlist.find_elements(By.TAG_NAME, "a")

	assert len(links) == 1
	links[0].click()
	assert driver.current_url == path.join(url_blog, blog_post)
