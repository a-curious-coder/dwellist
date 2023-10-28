import csv
import json
import logging
from datetime import datetime

import folium

from src.spareroom import (
    SpareRoom,
    append_new_rooms_to_spreadsheet,
    read_existing_rooms_from_spreadsheet,
)

# Set up logging with traceback
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s]\t%(message)s",
    handlers=[
        logging.FileHandler("log.txt"),
        logging.StreamHandler(),
    ],
)


with open("test_config.json") as config_file:
    config = json.load(config_file)


def print_settings():
    print("SETTINGS:")
    print(f"MIN_RENT_GBP: {config['MIN_RENT_GBP']}")
    print(f"MAX_RENT_GBP: {config['MAX_RENT_GBP']}")
    print(f"ROOMS_TO_SCRAPE: {config['ROOMS_TO_SCRAPE']}")
    print(f"AVAILABILITY_FROM_DAY: {config['AVAILABILITY_FROM_DAY']}")
    print(f"AVAILABILITY_FROM_MONTH: {config['AVAILABILITY_FROM_MONTH']}")
    print(f"AVAILABILITY_FROM_YEAR: {config['AVAILABILITY_FROM_YEAR']}")
    print(f"SEARCH_TERM: {config['SEARCH_TERM']}")
    print(f"FILENAME: {config['FILENAME']}")
    print(f"SEARCH_URL: {get_search_url()}")


def get_search_url():
    search_url = config["SEARCH_URL"].replace(
        "%MIN_RENT_GBP%", str(config["MIN_RENT_GBP"])
    )
    search_url = search_url.replace("%MAX_RENT_GBP%", str(config["MAX_RENT_GBP"]))
    search_url = search_url.replace(
        "%" + "ROOMS_TO_SCRAPE%", str(config["ROOMS_TO_SCRAPE"])
    )
    # Do this for AVAILABILITY_FROM_DAY, AVAILABILITY_FROM_MONTH, AVAILABILITY_FROM_YEAR
    search_url = search_url.replace(
        "%" + "AVAILABILITY_FROM_DAY" + "%", str(config["AVAILABILITY_FROM_DAY"])
    )
    search_url = search_url.replace(
        "%" + "AVAILABILITY_FROM_MONTH" + "%", str(config["AVAILABILITY_FROM_MONTH"])
    )
    search_url = search_url.replace(
        "%" + "AVAILABILITY_FROM_YEAR" + "%", str(config["AVAILABILITY_FROM_YEAR"])
    )
    search_url = search_url.replace(
        "%" + "SEARCH_TERM" + "%", str(config["SEARCH_TERM"])
    )
    return search_url


def parse_coordinates(coords):
    return [float(coord) for coord in coords[1:-1].split(",")]


def calculate_available_months(date_string):
    if date_string == "Now":
        return "Now"
    date = datetime.strptime(date_string, "%d %b %Y")
    today = datetime.today()
    days = (date - today).days
    if days <= 30:
        return "1 month"
    elif days <= 60:
        return "2 months"
    elif days <= 90:
        return "3 months"


def create_popup_content(row):
    room_prices = []
    for i in range(3):
        price_key = f"room_{i}_price"
        type_key = f"room_{i}_type"
        if row[price_key] != "":
            room_prices.append(
                f"<li>Room {i + 1}: £{row[price_key]} ({row[type_key]})</li>"
            )
    return f"""
        <div style="width: 200px;">
            <h3>{row["Area"]}</h3>
            <p><strong>Type:</strong> {row["Type"]}</p>
            <p><strong>Available:</strong> {row["Available"]}</p>
            <p><strong>Room Prices:</strong></p>
            <ul>
                {''.join(room_prices)}
            </ul>
            <a href="{row["url"]}" target="_blank">View Details</a>
        </div>
    """


def display_map():
    data = read_existing_rooms_from_spreadsheet(config["FILENAME"])
    data.fillna("", inplace=True)
    data["location_coords"] = data["location_coords"].apply(parse_coordinates)
    data["Latitude"] = data["location_coords"].apply(lambda x: x[0])
    data["Longitude"] = data["location_coords"].apply(lambda x: x[1])
    data["Available"] = data["Available"].apply(calculate_available_months)

    map_center = [data["Latitude"].mean(), data["Longitude"].mean()]
    my_map = folium.Map(location=map_center, zoom_start=12, tiles="cartodbdark_matter")

    for _, row in data.iterrows():
        popup_content = create_popup_content(row)
        icon_color = (
            "green"
            if row["date_scraped"] == datetime.today().strftime("%d-%m-%Y")
            else "orange"
        )
        icon = folium.Icon(
            color=icon_color, icon="star" if icon_color == "green" else "home"
        )
        folium.Marker(
            location=(row["Latitude"], row["Longitude"]),
            popup=folium.Popup(popup_content, max_width=250),
            tooltip=row["Area"],
            icon=icon,
        ).add_to(my_map)

    my_map.fit_bounds(my_map.get_bounds())

    tile_layers = [
        "cartodbdark_matter",
        "openstreetmap",
        "stamenterrain",
        "stamentoner",
        "stamenwatercolor",
        "cartodbpositron",
    ]

    for layer in tile_layers:
        folium.TileLayer(layer).add_to(my_map)

    folium.LayerControl().add_to(my_map)
    my_map.save("map.html")
    print("Map has been saved as 'map.html'.")


def main():
    print_settings()
    try:
        filename = config["FILENAME"]
        # Read the existing rooms from the spreadsheet
        existing_rooms_df = read_existing_rooms_from_spreadsheet(filename)

        # Instantiate SpareRoom and get new rooms
        spare_room = SpareRoom(config)
        new_rooms = spare_room.get_rooms(previous_rooms=existing_rooms_df)

        # Filter out rooms that already exist in the spreadsheet
        filtered_new_rooms = [
            room
            for room in new_rooms
            if existing_rooms_df.empty or room.id not in existing_rooms_df["id"].values
        ]

        # Append new rooms to the spreadsheet
        append_new_rooms_to_spreadsheet(existing_rooms_df, filtered_new_rooms, filename)
        logging.info(f"[+] Results saved: ./{filename}")
        display_map()
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        # traceback
        logging.exception(e)
    except KeyboardInterrupt:
        logging.info(" User interrupted.")


if __name__ == "__main__":
    main()
