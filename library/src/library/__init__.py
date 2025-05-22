import jinja2
import os, os.path as path

from jinja2.loaders import PackageLoader

pkgname: str
env: jinja2.Environment
def init(package_name: str | None):
    # to satisfy type checking
    assert package_name is not None
    global pkgname
    pkgname = package_name

    global env
    env = jinja2.Environment(
        loader=jinja2.PackageLoader(package_name),
        autoescape=True
    )

def get_dist_path(name: str) -> str:
    dist_path = path.join("dist", pkgname, name)
    dirname = path.dirname(dist_path)
    os.makedirs(dirname, exist_ok=True)
    return dist_path

def page(template_name: str, output_path: str | None=None, **kwargs):
    with open(get_dist_path(output_path or template_name), "w") as file:
        contents = env.get_template(template_name).render(**kwargs)
        file.write(contents)

__all__ = [
    "init",
    "page",
]
