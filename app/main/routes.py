import os
import csv
from flask import render_template, jsonify
from . import main
import sys


@main.route("/")
def index():
    print(
        "\n\n\n\n\n\n",
        file=sys.stderr,
    )
    try:
        print(f"Current WD: {os.getcwd()}", file=sys.stderr)
    except Exception:
        pass

    try:
        print(f"Current direc: {os.listdir()}", file=sys.stderr)
    except Exception:
        pass
    index_path = "index.html"
    # Does index.html exist?
    exist = os.path.exists(index_path)
    if not exist:
        print(f"NOT EXIST", file=sys.stderr)
    else:
        print(f"EXIST\n\n", file=sys.stderr)
    return render_template(index_path)


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
