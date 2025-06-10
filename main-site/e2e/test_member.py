from os import path

from conftest import url_member
from selenium.webdriver.common.by import By  # type: ignore


def test_member_social_links(member_page, driver):
	driver, _ = driver
	member_url = path.join(url_member, member_page)
	driver.get(member_url)

	links_par = driver.find_element(By.CSS_SELECTOR, ".links")
	links: list = links_par.find_elements(By.TAG_NAME, "a")

	assert len(links) == 3
