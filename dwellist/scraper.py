import traceback
import httpx
import asyncio
from pandas import DataFrame
import requests
from bs4 import BeautifulSoup as Soup
from dwellist.listing import Listing
from dwellist.logger import DwellistLogger
from dwellist.searchconstructor import SearchConstructor
from concurrent.futures import ThreadPoolExecutor


class SpareRoomScraper:
    """Scrape listings from SpareRoom"""

    domain = "https://www.spareroom.co.uk/flatshare/flatshare_detail.pl?flatshare_id="
    scraped_listings = []
    logger = DwellistLogger.get_logger()

    def __init__(self, config):
        search_constructor = SearchConstructor(config)
        self.url_search = search_constructor.get_search_url()
        self.config = config
        self.listings_to_scrape = config["listings_to_scrape"]
        self.session = requests.Session()
        self.already_logged = 0
        self.unavailable_listings = 0
        with self.session as session:
            request = session.get(self.url_search)
            request.raise_for_status()
            self.scraper = Soup(request.content, "lxml")
            self.logger.debug(f"URL: {request.url}")

        self.listings = []
        self.url = f"{request.url}offset="

        # ! New variables
        self.pages = []
        self.limit = self.config["listings_to_scrape"]

    def _get_soup(self, url: str) -> Soup:
        """
        Gets HTML from the URL then gives it to the Soup library to organise in a way that makes it easy to find the specific information we need.

        :param url: URL to get HTML from
        :return: Soup object
        """
        soup_object = None

        try:
            response = self.session.get(url, allow_redirects=False)
            response.raise_for_status()

            if response.status_code == 200:
                soup_object = Soup(response.content, "lxml")
            elif response.status_code == 302:
                self.logger.warning("302 redirect")
                traceback.print_stack()

        except requests.RequestException as e:
            self.logger.error("Request error: %s", e)

        return soup_object

    def _process_listing(
        self, new_listing: Soup, old_listings: DataFrame, logged_listings: list
    ) -> Listing:
        """
        Process a listing and return a Listing object

        :param listing: Soup object of listing
        :param previous_listings: DataFrame of previously scraped listings
        :param logged_listings: list of listing ids that have already been scraped
        :return: Listing object
        """
        # NOTE: Debugging purposes
        with open("listing.txt", "w", encoding="utf-8") as file:
            file.write(new_listing.prettify())

        try:
            listing_id = int(
                new_listing.prettify().split("flatshare_id=")[1].split("&")[0]
            )
        except (KeyError, ValueError, IndexError) as e:
            self.logger.error("Error parsing listing id: %s", e)

        if "Sorry, this listing is no longer available" in new_listing.prettify():
            self.logger.debug(f"Listing {listing_id} no longer available")
            self.unavailable_listings += 1
            return None

        add_new_listing = True
        if old_listings is not None and not old_listings.empty:
            add_new_listing = listing_id not in logged_listings

        if not add_new_listing:
            self.logger.debug(f"{listing_id} already logged")
            self.scraped_listings.append(listing_id)
            # If listing_id is in SCRAPED_ROOMS twice, something's wrong
            if self.scraped_listings.count(listing_id) > 1:
                self.logger.error(f"Listing {listing_id} already logged twice")
                return None
            self.already_logged += 1

        return Listing(new_listing, self.domain)

    def _get_listings_info(self, listings: Soup, previous_listings=None) -> list:
        """
        Get the listings from the search results page

        :param listings: Soup object of search results page
        :param previous_listings: DataFrame of previously scraped listings
        :return: list of Listing objects
        """
        # Create a list to store the futures
        listings = []
        scraped_listings = listings.find_all("article", class_="panel-listing-result")

        # Ensure listing-features is not included in scraped_listings
        scraped_listings = [
            listing
            for listing in scraped_listings
            if "listing-featured" not in str(listing)
        ]

        logged_listings = (
            previous_listings["id"].values.tolist()
            if not previous_listings.empty
            else []
        )

        futures = []
        # Create a ThreadPoolExecutor with a limited number of threads
        with ThreadPoolExecutor() as executor:
            # Process each listing in parallel
            for i, listing in enumerate(scraped_listings):
                listing_id = listing.prettify().split("flatshare_id=")[1].split("&")[0]
                if listing_id in logged_listings:
                    self.logger.debug(f"{listing_id} already logged")
                    self.already_logged += 1
                    continue
                listing_url = str(self.domain + listing_id)
                # Get the listing
                listing = Soup(requests.get(listing_url).content, "lxml")
                future = executor.submit(self._convert_to_listing, listing)
                futures.append(future)

        # Retrieve the results from the futures
        listings = []
        for future in futures:
            listing_obj = future.result()
            if listing_obj:
                listings.append(listing_obj)
        return listings

    def _count_available_listings(self, listings: Soup) -> int:
        """
        Count the number of available listings for scraping on the search results page

        :param listings: Soup object of search results page
        :return: number of available listings for scraping
        """
        num_available_listings = 0

        try:
            listings = listings.find_all("article", class_="panel-listing-result")
            # Exclude listing-featured listings
            listings = [
                listing
                for listing in listings
                if "listing-featured" not in str(listing)
            ]
            num_available_listings = len(listings)
        except Exception as e:
            self.logger.error("Error occurred: {}".format(e))
            self.logger.error(traceback.format_exc())
        return num_available_listings

    def get_total_results(self) -> int:
        """
        Get the total number of listings available to scrape

        :return: number of listings available to scrape
        """
        listings_per_page = 10
        try:
            page = self._get_soup(self.url)
            num_listings_on_last_page = self._count_available_listings(page)

            most_possible_listings = self._get_max_page_count() * listings_per_page
            available_listings = (
                most_possible_listings + num_listings_on_last_page
                if most_possible_listings < 1000
                else 1000
            )

            listings_to_scrape = min(self.listings_to_scrape, most_possible_listings)

            num_listings = (
                listings_to_scrape
                if listings_to_scrape < available_listings
                else available_listings
            )
            self.logger.info(f"Available Listings: {available_listings}")
            self.logger.info(f"Scrape Limit: {listings_to_scrape} listings")
            self.logger.info(f"Scraping {num_listings} listings")
        except Exception as e:
            self.logger.error("Failed to discover number of listings: {}".format(e))
        return num_listings

    def get_next_ten_listings(self, previous_listings=None, input=0) -> list:
        """
        Get the next ten listings from the search results page

        :param previous_listings: DataFrame of previously scraped listings
        :param input: A factor for a start index for the scraping process
        :return: list of Listing objects
        """
        start_index = input * 10
        end_index = start_index + 10

        if start_index >= self.listings_to_scrape:
            return None

        if input == 0:
            self.logger.info(
                f"{'New':^15}{'Exists':^15}{'Unavailable':^15}{'Total':^15}"
            )

        for i in range(start_index, min(end_index, self.listings_to_scrape), 10):
            url = f"{self.url}{i}"

            soup = self._get_soup(url)

            if soup:
                self.listings.extend(self._get_listings_info(soup, previous_listings))
                total_listings = (
                    len(self.listings) + self.already_logged + self.unavailable_listings
                )
                self.logger.info(
                    f"{len(self.listings):^15}{self.already_logged:^15}{self.unavailable_listings:^15}{total_listings:^15}"
                )
        return self.listings

    def _get_max_page_count(self) -> int:
        """
        Get the maximum number of pages to scrape represented by the offset value from the page

        The offset value represents the number of listings

        :return: maximum number of pages to scrape
        """
        # Find the navigation bar
        navbar = self.scraper.find("p", {"class": "navcurrent"})

        # Detect all values within strong tags
        navbar_item = navbar.findAll("strong")

        # Extract the number of listings from the second strong tag
        result_quantity = navbar_item[1]

        # NOTE: In some situations, it may say the maximum value of 1000 accompanied by a '+'
        # NOTE: SpareRoom will only ever show you, at most, 1000 results; even if there are more (it just means you need to be more specific with your search)
        listing_offset = int(
            result_quantity.string[:-1]
            if not result_quantity.string.endswith("+")
            else result_quantity.string[:-2]
        )

        return listing_offset

    async def scrape_all_pages(self, page_count: int) -> None:
        """
        Scrape all SpareRooms pages and store them in self.pages

        :param page_count: number of pages to scrape
        :return: None
        """

        results = []
        # Gather all spare_listing urls with offsets
        urls = [f"{self.url}{i}" for i in range(0, page_count * 10, 10)]

        # Using httpx to make async requests
        async with httpx.AsyncClient() as client:
            tasks = (client.get(url, timeout=20) for url in urls)
            results = await asyncio.gather(*tasks)

        # Convert the results to BS4 objects using lxml
        for result in results:
            soup = Soup(result.text, "lxml")
            self.pages.append(soup)

        self.logger.debug(f"Scraped {len(self.pages)} pages")

    def get_listing_ids(self, previous_listing_ids=[]):
        """
        Gets listing ids that are not already scraped and returns a list of listing ids in a quantity less than the predefined limit

        :param previous_listing_ids: list of listing ids that have already been scraped
        :return: list of listing ids
        """
        listing_ids = []
        for page_soup in self.pages:
            scraped_listings = page_soup.find_all(
                "article", class_="panel-listing-result"
            )

            # Ensure listing-features is not included in scraped_listings
            scraped_listings = [
                listing
                for listing in scraped_listings
                if "listing-featured" not in str(listing)
            ]

            # Check if each id is in the previous listings
            for index, listing in enumerate(scraped_listings):
                listing_id = int(
                    listing.prettify().split("flatshare_id=")[1].split("&")[0]
                )
                if listing_id not in previous_listing_ids:
                    listing_ids.append(listing_id)
                    if index == self.limit:
                        self.logger.info(f"Limit of {self.limit} reached")
                        break
                else:
                    self.logger.debug(f"{listing_id} already logged")

        return listing_ids

    async def scrape_all_listings(self, listing_ids: list) -> list:
        """
        Scrape all listings using the listing ids

        :param listing_ids: list of listing ids
        :return: list of Listing objects
        """
        # Using multiple threads, go through each soup object in pages and get the listing ids to create a list of urls
        # to scrape
        listings = []
        urls = [
            self.domain
            + "/flatshare/flatshare_detail.pl?flatshare_id="
            + str(listing_id)
            for listing_id in listing_ids
        ]
        async with httpx.AsyncClient() as client:
            tasks = (client.get(url, timeout=20) for url in urls)
            results = await asyncio.gather(*tasks)

        # Use lxml
        for result in results:
            soup = Soup(result.text, "lxml")
            listings.append(soup)

        return listings

    def process_listings(self, listings: list) -> list:
        """
        Process each listing

        :param listings: list of listings
        :return: list of processed listings
        """
        results = []
        for listing in listings:
            results.append(self._convert_to_listing(listing))
        return results

    def process_listings_threaded(self, listings: list) -> list:
        """
        Process each listing in parallel

        :param listings: list of listings
        :return: list of processed listings
        """
        with ThreadPoolExecutor() as executor:
            results = executor.map(self._convert_to_listing, listings)

        return results

    def _convert_to_listing(self, listing: Soup) -> Listing:
        """
        Convert a Beautiful Soup listing object to a Listing object

        :param listing: Soup object of listing
        :return: Listing object
        """
        return Listing(listing, self.domain)
