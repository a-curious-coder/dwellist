"""
Main file for collating data from SpareRoom
Dwellist is a tool for finding rooms on SpareRoom and visualising them on a map.

Barebones taken from afspies; modified, updated and improved by a-curious-coder
"""
import json
import logging
import os

from src.propertymap import RoomMapGenerator
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


def print_title():
    """Print the title from title.txt"""
    with open("title.txt", "r", encoding="utf-8") as title_file:
        title = title_file.read()
    print(title)


def main():
    """
    This function generates a property map, reads existing rooms from a spreadsheet,
    gets new rooms from SpareRoom, filters out rooms that already exist in the spreadsheet,
    appends new rooms to the spreadsheet, and generates a map of the new rooms.
    """
    os.system("cls" if os.name == "nt" else "clear")
    with open("test_config.json", "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    property_map = RoomMapGenerator(config)
    print_title()
    try:
        filename = config["filename"]
        # Read the existing rooms from the spreadsheet
        existing_rooms_df = read_existing_rooms_from_spreadsheet(filename)

        # Instantiate SpareRoom and get new rooms
        spare_room = SpareRoom(config)
        counter = 0
        # new_rooms = spare_room.get_rooms(previous_rooms=existing_rooms_df)
        while True:
            new_rooms = spare_room.get_next_ten_rooms(
                previous_rooms=existing_rooms_df, input=counter
            )
            if new_rooms is None:
                break
            # Filter out rooms that already exist in the spreadsheet
            filtered_new_rooms = [
                room
                for room in new_rooms
                if existing_rooms_df.empty
                or room.id not in existing_rooms_df["id"].values
            ]

            # Append new rooms to the spreadsheet
            append_new_rooms_to_spreadsheet(
                existing_rooms_df, filtered_new_rooms, filename
            )
            counter += 1
        logging.info("Results saved: ./%s", filename)
        property_map.generate_map()
    except KeyboardInterrupt:
        logging.info(" User interrupted.")
    finally:
        logging.info("Exiting.")


if __name__ == "__main__":
    main()
