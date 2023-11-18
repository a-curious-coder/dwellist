import os
import csv
from flask import render_template, jsonify
from . import main
import sys


def find_index_html(start_path="/dwellist/app"):
    for root, dirs, files in os.walk(start_path):
        if "index.html" in files:
            result = str(os.path.join(root, "index.html"))
            return result


@main.route("/")
def index():
    index_path = find_index_html()
    print(f"Found index.html in: {find_index_html()}", file=sys.stderr)

    # Does index.html exist?
    exist = os.path.exists(index_path)
    if not exist:
        print(f"{index_path} DOES NOT EXIST", file=sys.stderr)
    else:
        print(f"{index_path} DOES EXIST\n\n", file=sys.stderr)
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
