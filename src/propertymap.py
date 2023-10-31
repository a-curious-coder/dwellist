""" Generate a map of the rooms in the spreadsheet """
import json
import logging
from datetime import datetime

import folium
import pandas as pd


class RoomMapGenerator:
    """ Generate a map of the rooms in the spreadsheet """
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def _read_data(self):
        try:
            data = pd.read_csv(self.config["FILENAME"])
        except pd.errors.EmptyDataError:
            logging.error("No data found in %s", self.config["FILENAME"])

        data.fillna("", inplace=True)
        data["location_coords"] = data["location_coords"].apply(self._parse_coordinates)
        data["Latitude"] = data["location_coords"].apply(lambda x: x[0])
        data["Longitude"] = data["location_coords"].apply(lambda x: x[1])
        data["Available"] = data["Available"].apply(self._calculate_available_months)
        return data

    @staticmethod
    def _parse_coordinates(coords):
        return [float(coord) for coord in coords[1:-1].split(",")]

    @staticmethod
    def _calculate_available_months(date_string):
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

    def _create_popup_content(self, row):
        room_prices = []
        for i in range(3):
            price_key = f"room_{i}_price"
            type_key = f"room_{i}_type"
            if row[price_key] != "":
                room_prices.append(
                    f"<li>Room {i + 1}: £{row[price_key]} ({row[type_key]})</li>"
                )
        # get all values with key "image_{value}"
        image_links = [
            row[key]
            for key in row.keys()
            if key.startswith("image_") and row[key] != ""
        ]
        image_link = f'<img src="{image_links[0]}" alt="Image 1" width="200px">' if image_links else ""
        # write img tags for each image link
        # image_tags = [
        #     f'<img src="{image_link}" alt="Room {i + 1}" width="200px">'
        #     for i, image_link in enumerate(image_links)
        # ]
        return f"""
            <div style="width: 200px;">
                <h3>{row["Area"]}</h3>
                {image_link}
                <p><strong>Type:</strong> {row["Type"]}</p>
                <p><strong>Available:</strong> {row["Available"]}</p>
                <p><strong>Room Prices:</strong></p>
                <ul>
                    {''.join(room_prices)}
                </ul>
                <a href="{row["url"]}" target="_blank">View Details</a>
            </div>
        """

    def generate_map(self):
        """ Generate a map of the rooms in the spreadsheet """
        self.data = self._read_data()
        map_center = [self.data["Latitude"].mean(), self.data["Longitude"].mean()]
        my_map = folium.Map(location=map_center, zoom_start=12, tiles="cartodbdark_matter")

        for _, row in self.data.iterrows():
            popup_content = self._create_popup_content(row)
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
    """ Generate a map of the rooms in the spreadsheet """
    with open("test_config.json", "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
    room_map = RoomMapGenerator(config)
    room_map.generate_map()


if __name__ == "__main__":
    main()
