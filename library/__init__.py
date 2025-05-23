from typing import Any
import jinja2, markdown, frontmatter
import os, os.path as path
from .log import *

from jinja2.loaders import PackageLoader

pkgname: str
env: jinja2.Environment
base_path: str
def init(package_name: str | None):
    global pkgname, env, base_path

    # to satisfy type checking
    assert package_name is not None
    pkgname = package_name

    module_path = __import__(package_name).__path__[0]
    os.chdir(module_path)

    while module_path != "/":
        if path.exists(path.join(module_path, ".git")): break
        module_path = path.dirname(module_path)
    base_path = module_path

    env = jinja2.Environment(
        loader=jinja2.PackageLoader(package_name),
        autoescape=True
    )

    import atexit
    timer = LogTimer(f"Building {package_name!r}", f"Finished {package_name!r} in {{}}")
    timer.__enter__()
    atexit.register(timer.__exit__)

def dist_path_for(name: str) -> str:
    dist_path = path.join(base_path, "dist", pkgname, name)
    dirname = path.dirname(dist_path)
    os.makedirs(dirname, exist_ok=True)
    return dist_path

def page(template_name: str, output_path: str | None=None, **kwargs):
    with open(dist_path_for(output_path or template_name), "w") as file:
        contents = env.get_template(template_name).render(**kwargs)
        file.write(contents)

def markdown_to_html(file_path: str) -> tuple[Any, str]:
    with open(file_path, "r") as f:
        meta, content = frontmatter.parse(f.read())
        return meta, markdown.markdown(content)
