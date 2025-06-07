from os import path
from time import sleep

import pytest
from conftest import url_blog
from selenium.webdriver.common.action_chains import ActionChains  # type: ignore
from selenium.webdriver.common.by import By  # type: ignore


# helper for generating screenshots
def gen_screenshots(driver, dir, name, device):
	screenshot_path = path.join(dir,f"{device}.{name}.png")

	driver.get_full_page_screenshot_as_file(screenshot_path)

	assert path.exists(screenshot_path), f"Screenshot not saved at {screenshot_path}"

@pytest.fixture(scope="module", params=["desktop", "mobile"])
def screenshot_fixture(driver, screenshot_dir, request):
	if request.param == "desktop":
		driver.set_window_size(1024, 768)
	elif request.param == "mobile":
		driver.set_window_size(360, 800)

	return [driver, screenshot_dir, request.param]

def test_screenshot_home(screenshot_fixture):
	driver, screenshot_dir, device = screenshot_fixture
	driver.get("http://localhost:5123/")
	gen_screenshots(driver, screenshot_dir, "home", device)

def test_screenshot_blog(screenshot_fixture):
	driver, screenshot_dir, device = screenshot_fixture
	driver.get("http://localhost:5123/blog/")
	gen_screenshots(driver, screenshot_dir, "blog_overview", device)

def test_screenshot_blog_hover(screenshot_fixture):
	driver, screenshot_dir, device = screenshot_fixture

	blog_post = driver.find_element(By.CSS_SELECTOR, ".post-container")
	ActionChains(driver).move_to_element(blog_post).perform()
	sleep(1)  # Wait for any hover effects to take effect

	gen_screenshots(driver, screenshot_dir, "blog_overview_hover", device)

def test_screenshot_blog_post(blog_post, screenshot_fixture):
	driver, screenshot_dir, device = screenshot_fixture
	gallery_url = path.join(url_blog, blog_post)
	driver.get(gallery_url)

	gen_screenshots(driver, screenshot_dir, "blog_post", device)
