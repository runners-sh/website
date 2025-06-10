from os import path

from conftest import url_blog, url_member
from selenium.webdriver.common.by import By  # type: ignore


def test_member_social_links(member_page, driver):
	member_url = path.join(url_member, member_page)
	driver.get(member_url)

	links_par = driver.find_element(By.CSS_SELECTOR, ".links")
	links: list = links_par.find_elements(By.TAG_NAME, "a")

	assert len(links) == 3

def test_member_post_link(member_page, blog_post, driver):
	member_url = path.join(url_member, member_page)
	driver.get(member_url)

	postlist = driver.find_element(By.CSS_SELECTOR, ".post-list")
	links = postlist.find_elements(By.TAG_NAME, "a")

	assert len(links) == 1
	links[0].click()
	assert driver.current_url == path.join(url_blog, blog_post)
