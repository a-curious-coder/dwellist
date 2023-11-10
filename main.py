"""
Main file for collating data from SpareRoom
Dwellist is a tool for finding rooms on SpareRoom and visualising them on a map.

Barebones taken from afspies; modified, updated and improved by a-curious-coder
"""
import json
import os
import time
from math import ceil
from src.spareroom import (
    SpareRoom,
    append_new_rooms_to_spreadsheet,
    read_existing_rooms_from_spreadsheet,
)
from src.utilities import DwellistLogger, print_title
from concurrent.futures import ThreadPoolExecutor


def process_next_ten_rooms(args) -> bool:
    spare_room, existing_rooms_df, filename, counter = args
    new_rooms = spare_room.get_next_ten_rooms(
        previous_rooms=existing_rooms_df, input=counter
    )

    if new_rooms is None:
        return False

    # Remove rooms that are None
    new_rooms = [room for room in new_rooms if room is not None]

    # Filter out rooms that already exist in the spreadsheet
    filtered_new_rooms = [
        room
        for room in new_rooms
        if existing_rooms_df.empty or room.id not in existing_rooms_df["id"].values
    ]
    # Preprocess data;
    preprocess_data(filtered_new_rooms)
    # Append new rooms to the spreadsheet
    append_new_rooms_to_spreadsheet(existing_rooms_df, filtered_new_rooms, filename)
    return True

def get_new_rooms(scrapable_room_count, spare_room, existing_rooms_df, filename):
    counter = 0
    while counter <= ceil(scrapable_room_count // 10):
        process_next_ten_rooms((spare_room, existing_rooms_df, filename, counter))
        counter += 1


def main():
    """
    This function generates a property map, reads existing rooms from a spreadsheet,
    gets new rooms from SpareRoom, filters out rooms that already exist in the spreadsheet,
    appends new rooms to the spreadsheet, and generates a map of the new rooms.
    """
    logger = DwellistLogger.get_logger()
    with open("test_config.json", "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    os.system("cls" if os.name == "nt" else "clear")
    print_title()

    try:
        filename = config["filename"]
        # Read the existing rooms from the spreadsheet
        existing_rooms_df = read_existing_rooms_from_spreadsheet(filename)

        # Instantiate SpareRoom and get new rooms
        spare_room = SpareRoom(config)
        scrapable_room_count = spare_room.get_total_results()
        # divide by 10 because we get 10 results per page

        start_time = time.time()
        get_new_rooms(scrapable_room_count, spare_room, existing_rooms_df, filename)
        end_time = time.time()
        logger.info("SYNC Time elapsed: %s seconds", end_time - start_time)

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt.")
    except Exception as e:
        logger.exception("Exception occurred: %s", e)
    finally:
        logger.info("Exiting.")


if __name__ == "__main__":
    main()
