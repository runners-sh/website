from os import path
from time import sleep

from conftest import url_blog
from selenium.webdriver.common.action_chains import ActionChains  # type: ignore
from selenium.webdriver.common.by import By  # type: ignore


# helper for generating screenshots
def gen_screenshots(driver, dir, name, mobile):
	screenshot_path = path.join(dir,f"{"mobile" if mobile else "desktop"}.{name}.png")

	driver.get_full_page_screenshot_as_file(screenshot_path)

	assert path.exists(screenshot_path), f"Screenshot not saved at {screenshot_path}"



def test_screenshot_home(driver, screenshot_dir):
	driver.get("http://localhost:5123/")

	driver.set_window_size(1024, 768)
	gen_screenshots(driver, screenshot_dir, "home", mobile=False)
	driver.set_window_size(360, 800)  # smasnug galala S20
	gen_screenshots(driver, screenshot_dir, "home", mobile=True)

def test_screenshot_blog(driver, screenshot_dir):
	driver.get("http://localhost:5123/blog/")

	driver.set_window_size(1024, 768)
	gen_screenshots(driver, screenshot_dir, "blog", mobile=False)
	driver.set_window_size(360, 800)
	gen_screenshots(driver, screenshot_dir, "blog", mobile=True)

def test_screenshot_blog_hover(driver, screenshot_dir):
	driver.get("http://localhost:5123/blog/")

	driver.set_window_size(1024, 768)
	blog_post = driver.find_element(By.CSS_SELECTOR, ".post-container")
	ActionChains(driver).move_to_element(blog_post).perform()
	sleep(1)  # Wait for any hover effects to take effect

	gen_screenshots(driver, screenshot_dir, "blog_hover", mobile=False)

	driver.set_window_size(360, 800)
	blog_post = driver.find_element(By.CSS_SELECTOR, ".post-container")
	ActionChains(driver).move_to_element(blog_post).perform()
	sleep(1)  # Wait for any hover effects to take effect

	gen_screenshots(driver, screenshot_dir, "blog_hover", mobile=True)

def test_screenshot_blog_post(blog_post, driver, screenshot_dir):
	gallery_url = path.join(url_blog, blog_post)
	driver.get(gallery_url)

	driver.set_window_size(1024, 768)
	gen_screenshots(driver, screenshot_dir, "blog_post", mobile=False)
	driver.set_window_size(360, 800)
	gen_screenshots(driver, screenshot_dir, "blog_post", mobile=True)
