from conftest import url_blog, url_blog_gallery, url_blog_headers
from selenium.webdriver.common.by import By  # type: ignore


def test_post_list(driver):
	driver.get(url_blog)
	postlist = driver.find_element(By.CSS_SELECTOR, ".post-list")
	links = postlist.find_elements(By.TAG_NAME, "a")

	assert len(links) == 2
	urls = [x.get_attribute("href") for x in links]

	assert url_blog_gallery in urls
	assert url_blog_headers in urls
