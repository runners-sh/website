# ruff: noqa: F401
import os
import shutil
import subprocess
import sys
import tempfile
from os import path

import pytest
from selenium import webdriver  # type: ignore

url_base = "http://localhost:5123"
url_home = f"{url_base}/"
url_blog = f"{url_base}/blog/"
url_member = f"{url_base}/member/"

@pytest.fixture(scope="session")
def mock_fs(request):
	mod_dir = __import__("main-site").__path__[0]
	mock_content_path = "main-site/e2e/mock-content"
	tmp_dir = path.join(mod_dir, os.pardir, "__tmp_testing_site")
	shutil.copytree(mod_dir, tmp_dir, dirs_exist_ok=True)

	for src in os.listdir(mock_content_path):
		dst = path.join(tmp_dir, src)
		shutil.rmtree(dst)
		shutil.copytree(
			path.join(mock_content_path, src),
			dst,
			ignore=shutil.ignore_patterns('*.pyc', '__pycache__', 'e2e')
		)
	subprocess.run([sys.executable, "-m", "__tmp_testing_site", "build"], shell=True, check=True)

	yield
	shutil.rmtree(tmp_dir)

@pytest.fixture(scope="session")
def serve(mock_fs):
	proc = subprocess.Popen(
		[sys.executable, "-m", "__tmp_testing_site", "serve"],
		stdout=subprocess.DEVNULL,
		stderr=subprocess.DEVNULL,
	)

	yield

	proc.terminate()
	proc.wait()


@pytest.fixture(scope="session")
def driver(serve):
	options = webdriver.FirefoxOptions()
	profile = webdriver.FirefoxProfile()

	profile.set_preference("ui.prefersReducedMotion", 1)

	options.profile = profile
	options.add_argument("--headless")
	driver = webdriver.Firefox(options=options)
	driver.implicitly_wait(3)

	yield driver

	driver.quit()

@pytest.fixture(scope="module", params=["desktop", "mobile"])
def driver_multires(driver, request):
	if request.param == "mobile":
		driver.set_window_size(360, 800)
	else:
		driver.set_window_size(1024, 768)

	return [driver, request.param]

@pytest.fixture(scope="session")
def screenshot_dir(request):
	screenshot_dir = "./dist/screenshots"
	os.makedirs(screenshot_dir, exist_ok=True)

	return screenshot_dir

@pytest.fixture(scope="session")
def blog_post():
	return "gallery"

@pytest.fixture(scope="session")
def member_page():
	return "johndoe"
