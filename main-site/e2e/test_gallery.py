import subprocess
import sys
from time import sleep

import pytest
from selenium import webdriver  # type: ignore
from selenium.webdriver.common.by import By  # type: ignore

url_base = "http://localhost:5123"
url_post = f"{url_base}/blog/gallery"


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


def test_toc_heading_link_layers(driver):
	driver.get(url_post)

	table_of_contents = driver.find_element(
		By.XPATH,
		""".//main//aside//div[contains(concat(" ",normalize-space(@class)," ")," toc ")]""",
	)

	header_link = table_of_contents.find_element(By.LINK_TEXT, "Heading 1")
	header_link.click()
	assert driver.current_url == f"{url_post}#heading-1"

	header_link = table_of_contents.find_element(By.LINK_TEXT, "Heading 2")
	header_link.click()
	assert driver.current_url == f"{url_post}#heading-2"

	header_link = table_of_contents.find_element(By.LINK_TEXT, "Heading 3")
	header_link.click()
	assert driver.current_url == f"{url_post}#heading-3"

	header_link = table_of_contents.find_element(By.LINK_TEXT, "Heading 4")
	header_link.click()
	assert driver.current_url == f"{url_post}#heading-4"

	header_link = table_of_contents.find_element(By.LINK_TEXT, "Heading 5")
	header_link.click()
	assert driver.current_url == f"{url_post}#heading-5"

	header_link = table_of_contents.find_element(By.LINK_TEXT, "Heading 6")
	header_link.click()
	assert driver.current_url == f"{url_post}#heading-6"
