
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
env = Environment(
    loader=FileSystemLoader("../test"), #PackageLoader("test"),
    autoescape=select_autoescape()
)

template = env.get_template("jinjaHTML.html")

my_dict = {
    "name": "HAMMAD",
    "lucky_number": 777,
    "cont_num": 3.1415926519793,
    "description": "Some Description Dumb",
}

rendered_template = template.render(c=my_dict)

print(rendered_template)
