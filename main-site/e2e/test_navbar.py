import subprocess
import sys
from time import sleep

import pytest
from selenium import webdriver  # type: ignore
from selenium.webdriver.common.by import By  # type: ignore

url_base = "http://localhost:5123"
url_home = f"{url_base}/"
url_blog = f"{url_base}/blog/"


@pytest.fixture
def driver():
	proc = subprocess.Popen(
		[sys.executable, "-m", "main-site", "serve"],
		stdout=subprocess.DEVNULL,
		stderr=subprocess.DEVNULL,
	)
	sleep(0.5)

	options = webdriver.FirefoxOptions()
	options.add_argument("--headless")
	driver = webdriver.Firefox(options=options)
	driver.implicitly_wait(5)

	yield driver

	proc.kill()
	driver.quit()


def test_navbar_urls(driver):
	driver.get(url_base)

	navbar = driver.find_element(By.XPATH, "//nav")
	blog_link = navbar.find_element(By.LINK_TEXT, "blog")
	blog_link.click()
	assert driver.current_url == url_blog

	navbar = driver.find_element(By.XPATH, "//nav")
	home_link = navbar.find_element(By.LINK_TEXT, "home")
	home_link.click()
	assert driver.current_url == url_home
