from os import path
from time import sleep

from conftest import url_blog, url_blog_gallery, url_member_johndoe
from selenium.webdriver.common.action_chains import ActionChains  # type: ignore
from selenium.webdriver.common.by import By  # type: ignore


# helpers for generating screenshots
def page_screenshot(driver, dir, name, device):
	screenshot_path = path.join(dir, f"{device}.{name}.png")
	driver.get_full_page_screenshot_as_file(screenshot_path)
	assert path.exists(screenshot_path), f"Screenshot not saved at {screenshot_path}"


def element_screenshot(driver, dir, name, device, element):
	screenshot_path = path.join(dir, f"{device}.{name}.png")
	element.screenshot(screenshot_path)
	assert path.exists(screenshot_path), f"Screenshot not saved at {screenshot_path}"


def window_screenshot(driver, dir, name, device):
	screenshot_path = path.join(dir, f"{device}.{name}.png")
	driver.get_screenshot_as_file(screenshot_path)
	assert path.exists(screenshot_path), f"Screenshot not saved at {screenshot_path}"


def test_screenshot_home(driver_multires, screenshot_dir):
	driver, device = driver_multires
	driver.get("http://localhost:5123/")

	page_screenshot(driver, screenshot_dir, "home", device)


def test_screenshot_blog_overview(driver_multires, screenshot_dir):
	driver, device = driver_multires
	driver.get(url_blog)

	page_screenshot(driver, screenshot_dir, "blog_overview", device)


def test_screenshot_blog_overview_item(driver_multires, screenshot_dir):
	driver, device = driver_multires
	driver.get(url_blog)

	blog_post = driver.find_element(By.CSS_SELECTOR, ".post-list > li")
	ActionChains(driver).move_to_element(blog_post).perform()
	sleep(0.3)  # Wait for any hover effects to take effect

	element_screenshot(driver, screenshot_dir, "blog_overview_item_hover", device, blog_post)


def test_screenshot_blog_post(driver_multires, screenshot_dir):
	driver, device = driver_multires
	driver.get(url_blog_gallery)

	page_screenshot(driver, screenshot_dir, "blog_post", device)


def test_screenshot_blog_post_barcode(driver_multires, screenshot_dir):
	driver, device = driver_multires
	driver.get(url_blog_gallery)

	barcode = driver.find_element(By.CSS_SELECTOR, ".main-barcode")
	segment = barcode.find_element(By.CSS_SELECTOR, ".segment")
	ActionChains(driver).move_to_element(segment).perform()
	sleep(0.3)  # Wait for any hover effects to take effect

	window_screenshot(driver, screenshot_dir, "blog_post_barcode", device)


def test_screenshot_member(driver_multires, screenshot_dir):
	driver, device = driver_multires
	driver.get(url_member_johndoe)

	page_screenshot(driver, screenshot_dir, "member_page", device)
