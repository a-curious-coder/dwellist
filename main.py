"""
Main file for collating data from SpareRoom
Dwellist is a tool for finding listings on SpareRoom and visualising them on a map.

Barebones taken from afspies; modified, updated and improved by a-curious-coder
"""
import json
import os
import time
from dwellist.scraper import SpareRoomScraper
from dwellist.logger import DwellistLogger
from dwellist.utilities import (
    print_title,
    add_new_listings,
    get_existing_listings,
)
import asyncio

logger = DwellistLogger.get_logger()


def process_next_ten_listings(args) -> bool:
    spare_listing, existing_listings_df, filepath, counter = args
    new_listings = spare_listing.get_next_ten_listings(
        previous_listings=existing_listings_df, input=counter
    )

    if new_listings is None:
        return False

    # Remove listings that are None
    new_listings = [listing for listing in new_listings if listing is not None]

    # Filter out listings that already exist in the spreadsheet
    filtered_new_listings = [
        listing
        for listing in new_listings
        if existing_listings_df.empty
        or listing.id not in existing_listings_df["id"].values
    ]
    # Append new listings to the spreadsheet
    get_existing_listings(existing_listings_df, filtered_new_listings, filepath)
    return True


def get_new_listings(scraper, existing_listings_df, filename):
    counter = 0
    while process_next_ten_listings((scraper, existing_listings_df, filename, counter)):
        counter += 1


def scrape_listings_slow(config):
    # ! Get existing listings locally
    filename = config["filename"]
    filepath = os.path.join(os.getcwd(), "dwellist\\data\\" + filename)
    # Read the existing listings from the spreadsheet
    existing_listings_df = get_existing_listings(filepath)

    # ! Get new listings from SpareRoom
    # Instantiate SpareRoom and get new listings
    scraper = SpareRoomScraper(config)

    # ! Get new listings from SpareRoom
    get_new_listings(scraper, existing_listings_df, filepath)


def scrape_listings_fast(config):
    scraper = SpareRoomScraper(config)
    # ! Get number of pages we want to scrape
    scrapable_listing_count = scraper.get_total_results()
    page_count = (
        scrapable_listing_count // 10
        if scrapable_listing_count < config["listings_to_scrape"]
        else config["listings_to_scrape"] // 10
    )

    # ! Scrape the pages
    asyncio.run(scraper.scrape_all_pages(page_count))

    # ! Create filepath for listings
    filename = config["filename"]
    filepath = os.path.join(os.getcwd(), "dwellist\\data\\" + filename)

    # ! Get existing listing ids
    existing_listings_df = get_existing_listings(filepath)
    existing_listing_ids = (
        existing_listings_df["id"].values.tolist()
        if not existing_listings_df.empty
        else []
    )

    # ! Get new listing ids from SpareRoom
    listing_ids = scraper.get_listing_ids(existing_listing_ids)

    if len(listing_ids) > 0:
        # ! Scrape all new listing listings
        start = time.perf_counter()

        listings = asyncio.run(scraper.scrape_all_listings(listing_ids))

        end = time.perf_counter()
        elapsed = f"{end - start:.2f}"
        logger.debug("Scrape time: %s seconds", elapsed)

        # ! Preprocess each listing listing and save each to spreadsheet
        logger.debug(f"Processing {len(listings)} listings")
        results = scraper.process_listings_threaded(listings)

        # TODO: Remove this when saving each property to spreadsheet
        filtered_new_listings = [
            listing
            for listing in results
            if existing_listings_df.empty
            or listing.id not in existing_listings_df["id"].values
        ]
        add_new_listings(existing_listings_df, filtered_new_listings, filepath)


def test_scrape_listings_processes(config):
    # If there are existing listings, rename the file to a backup
    filename = config["filename"]
    filepath = os.path.join(os.getcwd(), "dwellist\\data\\" + filename)
    if os.path.exists(filepath):
        os.rename(filepath, filepath + ".bak")

    # ! Scrape listings slow
    start = time.perf_counter()
    scrape_listings_slow(config)

    end = time.perf_counter()
    elapsed = f"{end - start:.2f}"
    logger.info("Slow process time: %s seconds", elapsed)

    # Delete the new file
    os.remove(filepath)

    # ! Scrape listings fast
    start = time.perf_counter()
    scrape_listings_fast(config)
    end = time.perf_counter()
    elapsed = f"{end - start:.2f}"
    logger.info("Fast process time: %s seconds", elapsed)

    # Delete the new file
    os.remove(filepath)

    # Rename the backup file to the original filename
    os.rename(filepath + ".bak", filepath)


def main():
    """
    This function generates a property map, reads existing listings from a spreadsheet,
    gets new listings from SpareRoom, filters out listings that already exist in the spreadsheet,
    appends new listings to the spreadsheet, and generates a map of the new listings.
    """
    test_processes = False
    try:
        with open("test_config.json", "r", encoding="utf-8") as config_file:
            config = json.load(config_file)

        os.system("cls" if os.name == "nt" else "clear")
        print_title()
        if test_processes:
            test_scrape_listings_processes(config)
        # ! Scrape listings fast
        start = time.perf_counter()
        scrape_listings_fast(config)
        end = time.perf_counter()
        elapsed = f"{end - start:.2f}"
        logger.info("Listings scraped: %s seconds", elapsed)

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt.")
    except Exception as e:
        logger.exception("Exception occurred: %s", e)
    finally:
        logger.info("Exiting.")


if __name__ == "__main__":
    main()
