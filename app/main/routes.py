import os
import csv
from flask import render_template, jsonify
from . import main
import sys


@main.route("/")
def index():
    return render_template("index.html")


def read_csv():
    """Load data as a list of dictionaries"""
    data_path = os.path.join(os.getcwd(), "dwellist/data/spareroom_listing.csv")
    # Read CSV file
    with open(data_path, "r", encoding="utf-8") as csv_file:
        data = list(csv.DictReader(csv_file))

    # Move back to app directory
    return data


# Route to fetch marker data
@main.route("/get_markers")
def get_markers():
    """Return the marker data as a JSON object"""
    data = read_csv()
    return jsonify(data)
