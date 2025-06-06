import os
from time import sleep

from selenium.webdriver.common.action_chains import ActionChains  # type: ignore
from selenium.webdriver.common.by import By  # type: ignore


def test_screenshot_home(driver, screenshot_dir):
	driver.get("http://localhost:5123/")

	screenshot_path = os.path.join(screenshot_dir, "home.png")
	driver.save_screenshot(screenshot_path)
	assert os.path.exists(screenshot_path), f"Screenshot not saved at {screenshot_path}"

def test_screenshot_blog(driver, screenshot_dir):
	driver.get("http://localhost:5123/blog/")

	screenshot_path = os.path.join(screenshot_dir, "blog.png")
	driver.save_screenshot(screenshot_path)
	assert os.path.exists(screenshot_path), f"Screenshot not saved at {screenshot_path}"

def test_screenshot_blog_hover(driver, screenshot_dir):
	driver.get("http://localhost:5123/blog/")

	blog_post = driver.find_element(By.CSS_SELECTOR, ".post-container")
	ActionChains(driver).move_to_element(blog_post).perform()
	sleep(1)  # Wait for any hover effects to take effect

	screenshot_path = os.path.join(screenshot_dir, "blog_hover.png")
	driver.save_screenshot(screenshot_path)
	assert os.path.exists(screenshot_path), f"Screenshot not saved at {screenshot_path}"
