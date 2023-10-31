import json

from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


# Route to fetch marker data
@app.route("/get_markers")
def get_markers():
    # Code to scrape and preprocess data (replace this with your actual logic)
    markers_data = [
        {"lat": 51.505, "lng": -0.09, "category": "restaurant"},
        {"lat": 51.515, "lng": -0.1, "category": "hotel"},
        {"lat": 51.525, "lng": -0.11, "category": "park"}
        # Add more marker data as needed
    ]
    return json.dumps(markers_data)


if __name__ == "__main__":
    app.run(debug=True)
