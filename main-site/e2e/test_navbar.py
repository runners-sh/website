from conftest import url_base, url_blog, url_home
from selenium.webdriver.common.by import By  # type: ignore


def test_navbar_root_solrunners_url(driver):
	driver, _ = driver
	driver.get(url_base)

	navbar = driver.find_element(By.XPATH, "//nav")
	home_link = navbar.find_element(By.LINK_TEXT, "root@solrunners ~#")
	home_link.click()


def test_navbar_home_url(driver):
	driver, _ = driver
	driver.get(url_base)

	navbar = driver.find_element(By.XPATH, "//nav")
	home_link = navbar.find_element(By.LINK_TEXT, "home")
	home_link.click()
	assert driver.current_url == url_home


def test_navbar_blog_url(driver):
	driver, _ = driver
	driver.get(url_base)

	navbar = driver.find_element(By.XPATH, "//nav")
	home_link = navbar.find_element(By.LINK_TEXT, "blog")
	home_link.click()
	assert driver.current_url == url_blog
