import csv

from flask import Flask, jsonify, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


def read_csv():
    """Load data as a list of dictionaries"""
    with open("test.csv", "r", encoding="utf-8") as csv_file:
        data = list(csv.DictReader(csv_file))
    return data


# Route to fetch marker data
@app.route("/get_markers")
def get_markers():
    """Return the marker data as a JSON object"""
    data = read_csv()
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
