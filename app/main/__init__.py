from flask import Blueprint
import os

# TODO: Maybe do something more conventional here in future
absolute_templates_path = os.path.join(os.getcwd(), "\\app\\templates")

main = Blueprint("main", __name__, template_folder=absolute_templates_path)

from . import routes
