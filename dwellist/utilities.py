from pandas import DataFrame, read_csv
from pandas import concat as concatenate
from pandas.errors import EmptyDataError
from dwellist.listing import Listing


def print_title():
    """Print the title from title.txt"""
    with open("misc/title.txt", "r", encoding="utf-8") as title_file:
        title = title_file.read()
    print(title)


def get_existing_listings(file_path: str) -> DataFrame:
    """
    Get existing listings from csv

    :param file_path: path to csv
    :return: DataFrame of existing listings
    """
    try:
        df = read_csv(file_path)
    except (FileNotFoundError, EmptyDataError):
        df = DataFrame()
    return df


def add_new_listing(
    existing_listings: DataFrame, new_listing: Listing, file_path: str
) -> None:
    """
    Add a new listing to the listings DataFrame

    :param existing_listings: DataFrame of existing listings
    :param new_listing: Listing object of new listing
    :param file_path: path to csv
    :return: None
    """
    new_df = DataFrame([new_listing.__dict__])

    if existing_listings is None or existing_listings.empty:
        combined_df = new_df
    else:
        combined_df = concatenate([existing_listings, new_df], ignore_index=True)

    reordered_columns = _reorder_columns(combined_df.columns)
    combined_df = combined_df[reordered_columns]

    combined_df.to_csv(file_path, index=False)


def add_new_listings(
    existing_listings: DataFrame, new_listings: list, file_path: str
) -> None:
    """
    Add new listings to the listings DataFrame

    :param existing_listings: DataFrame of existing listings
    :param new_listings: list of Listing objects of new listings
    :param file_path: path to csv
    :return: None
    """
    new_listings_df = DataFrame([new_listing.__dict__ for new_listing in new_listings])

    # If there are no existing listings, just use the new listings
    if existing_listings is not None or not existing_listings.empty:
        updated_listings_df = concatenate(
            [existing_listings, new_listings_df], ignore_index=True
        )

    # Get the reordered column headers order
    reordered_columns = _reorder_columns(updated_listings_df.columns)
    # Reorder the columns in the DataFrame
    updated_listings_df = updated_listings_df[reordered_columns]
    # Save the DataFrame to the csv
    updated_listings_df.to_csv(file_path, index=False)


def _reorder_columns(columns: list) -> list:
    """
    Reorder columns

    :param columns: list of columns
    :return: list of reordered columns
    """
    listing_columns = [col for col in columns if col.startswith("listing_")]
    deposit_columns = [col for col in columns if col.startswith("deposit")]
    image_columns = [col for col in columns if col.startswith("image")]
    non_listing_columns = [
        col
        for col in columns
        if (col not in listing_columns + deposit_columns + image_columns)
    ]

    reordered_columns = non_listing_columns
    reordered_columns.extend(listing_columns)
    reordered_columns.extend(deposit_columns)
    reordered_columns.extend(image_columns)

    return reordered_columns
