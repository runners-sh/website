from typing import Any
import jinja2, markdown, frontmatter
import os, os.path as path, shutil
from .log import *

from jinja2.loaders import PackageLoader

pkgname: str
env: jinja2.Environment
base_path: str
dist_path: str
def init(package_name: str | None):
    global pkgname, env, base_path, dist_path

    timer = LogTimer(f"Building {package_name!r}", f"Finished {package_name!r} in {{}}")
    timer.__enter__()
    import atexit
    atexit.register(timer.__exit__)

    # to satisfy type checking
    assert package_name is not None
    pkgname = package_name

    module_path = __import__(package_name).__path__[0]
    os.chdir(module_path)

    while module_path != "/":
        if path.exists(path.join(module_path, ".git")): break
        module_path = path.dirname(module_path)
    base_path = module_path
    dist_path = path.join(base_path, "dist")

    shutil.rmtree(dist_path, ignore_errors=True)

    env = jinja2.Environment(
        loader=jinja2.PackageLoader(package_name),
        autoescape=True
    )

def dist_path_for(name: str) -> str:
    p = path.join(dist_path, pkgname, name)
    dirname = path.dirname(p)
    os.makedirs(dirname, exist_ok=True)
    return p

def page(template_name: str, output_path: str | None=None, **kwargs):
    with open(dist_path_for(output_path or template_name), "w") as file:
        contents = env.get_template(template_name).render(**kwargs)
        file.write(contents)

def markdown_to_html(file_path: str) -> tuple[Any, str]:
    with open(file_path, "r") as f:
        meta, content = frontmatter.parse(f.read())
        return meta, markdown.markdown(content)

from . import common
