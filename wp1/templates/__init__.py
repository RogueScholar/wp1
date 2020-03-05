from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2 import select_autoescape


def commas(n):
  return "{:,d}".format(n)


env = Environment(
    loader=PackageLoader("wp1", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)
env.filters["commas"] = commas
