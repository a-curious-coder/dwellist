from flask import Blueprint
import os

# TODO: Maybe do something more conventional here in future

main = Blueprint("main", __name__)

from . import routes
