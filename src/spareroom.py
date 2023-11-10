import datetime
from src.utilities import DwellistLogger
import traceback

import pandas as pd
import requests
from bs4 import BeautifulSoup
import concurrent.futures

from src.searchconstructor import SearchConstructor
from concurrent.futures import ThreadPoolExecutor


class SpareRoom:
    """Scrape rooms from SpareRoom"""

    DOMAIN = "https://www.spareroom.co.uk"
    URL_ROOMS = f"{DOMAIN}/flatshare"
    SCRAPED_ROOMS = []

    def __init__(self, config):
        search_constructor = SearchConstructor(config)
        self.URL_SEARCH = search_constructor.get_search_url()
        self.config = config
        self.rooms_to_scrape = config["rooms_to_scrape"]
        self.logger = DwellistLogger.get_logger()
        self.session = requests.Session()
        self.already_logged = 0
        self.unavailable_rooms = 0
        with requests.Session() as session:
            request = session.get(self.URL_SEARCH)
            request.raise_for_status()
            self.scraper = BeautifulSoup(request.content, "lxml")
        self.logger.debug(f"URL: {request.url}")

        self.rooms = []
        self.room_offset = self._get_room_offset()
        self.url = f"{request.url}offset="

    def _get_soup(self, url):
        """In laymans terms, this function gets the HTML from the URL and collates/returns a BeautifulSoup object
        :param url: URL to get HTML from
        :return: BeautifulSoup object
        """
        try:
            response = self.session.get(url, allow_redirects=False)
            response.raise_for_status()
            if response.status_code == 200:
                return BeautifulSoup(response.content, "lxml")
            elif response.status_code == 302:
                self.logger.warning("302 redirect")
                traceback.print_stack()
                return None
        except requests.RequestException as e:
            self.logger.error("Request error: %s", e)
        return None

    def process_room(self, room, previous_rooms, logged_rooms):
        # NOTE: Debugging purposes
        with open("room_debug/room.txt", "w", encoding="utf-8") as file:
            file.write(room.prettify())

        try:
            room_id = int(room.prettify().split("flatshare_id=")[1].split("&")[0])
        except (KeyError, ValueError, IndexError) as e:
            self.logger.error("Error parsing room id: %s", e)

        if "Sorry, this room is no longer available" in room.prettify():
            # self.logger.warning(f"Room {room_id} no longer available")
            self.unavailable_rooms += 1
            return None

        add_room = True
        if previous_rooms is not None and not previous_rooms.empty:
            add_room = room_id not in logged_rooms

        if add_room:
            room_obj = Room(room, self.DOMAIN)  # Assuming Room class instantiation
            if room_obj is not None:
                return room_obj
        else:
            self.logger.debug(f"{room_id} already logged")
            self.SCRAPED_ROOMS.append(room_id)
            # If room_id is in SCRAPED_ROOMS twice, something's wrong
            if self.SCRAPED_ROOMS.count(room_id) > 1:
                self.logger.error(f"Room {room_id} already logged twice")
                return None
            self.already_logged += 1

    def _get_rooms_info(self, rooms_soup, previous_rooms=None):
        # Create a list to store the futures
        rooms = []
        scraped_rooms = rooms_soup.find_all("article", class_="panel-listing-result")

        # Ensure listing-features is not included in scraped_rooms
        scraped_rooms = [
            room for room in scraped_rooms if "listing-featured" not in str(room)
        ]

        logged_rooms = (
            previous_rooms["id"].values.tolist()
            if not previous_rooms.empty
            else pd.DataFrame()
        )
        futures = []
        # Create a ThreadPoolExecutor with a limited number of threads
        with ThreadPoolExecutor() as executor:
            # Process each room in parallel
            for i, room in enumerate(scraped_rooms):
                future = executor.submit(
                    self.process_room, room, previous_rooms, logged_rooms
                )
                futures.append(future)

        # Retrieve the results from the futures
        rooms = []
        for future in futures:
            room_obj = future.result()
            if room_obj:
                rooms.append(room_obj)
        return rooms

    def _count_available_rooms(self, rooms_soup):
        """Count the number of available rooms for scraping on the search results page
        :param rooms_soup: BeautifulSoup object of search results page
        :return: number of available rooms for scraping
        """
        num_available_rooms = 0

        try:
            rooms = rooms_soup.find_all("article", class_="panel-listing-result")
            # Ensure class featured-listing is not included in rooms
            rooms = [room for room in rooms if "listing-featured" not in str(room)]
            num_available_rooms = len(rooms)
        except AttributeError:
            self.logger.debug("The number of rooms is on a 10 (e.g. 990 or 1000)")
        except Exception as e:
            self.logger.error("Error occurred: {}".format(e))
            self.logger.error(traceback.format_exc())

        return num_available_rooms

    def get_total_results(self):
        rooms_to_scrape = min(self.rooms_to_scrape, (self.room_offset * 10))
        soup = self._get_soup(self.url)
        if soup:
            num_rooms = self._count_available_rooms(soup)
            num_rooms = num_rooms + (rooms_to_scrape)
            self.logger.info(f"Scraping {num_rooms} rooms.")
        else:
            self.logger.error("Failed to fetch search results")
        return num_rooms

    def get_next_ten_rooms(self, previous_rooms=None, input=0) -> list:
        """Get the next ten rooms from the search results page
        :param previous_rooms: DataFrame of previously scraped rooms
        :param input: A factor for a start index for the scraping process
        :return: list of Room objects
        """
        start_index = input * 10
        end_index = start_index + 10
        num_rooms = 0

        if start_index >= self.rooms_to_scrape:
            self.logger.info("Scraping process complete")
            return None

        if input == 0:
            self.logger.info(
                f"{'New':^15}{'Exists':^15}{'Unavailable':^15}{'Total':^15}"
            )

        for i in range(start_index, min(end_index, self.rooms_to_scrape), 10):
            url = f"{self.url}{i}"

            soup = self._get_soup(url)

            if soup:
                self.rooms.extend(self._get_rooms_info(soup, previous_rooms))
                total_rooms = (
                    len(self.rooms) + self.already_logged + self.unavailable_rooms
                )
                self.logger.info(
                    f"{len(self.rooms):^15}{self.already_logged:^15}{self.unavailable_rooms:^15}{total_rooms:^15}"
                )
        return self.rooms

    def _get_room_offset(self):
        navbar = self.scraper.find("p", {"class": "navcurrent"})
        navbar_item = navbar.findAll("strong")
        # Get the number of 'results'
        # NOTE: In some situations, it may say the maximum of 1000.
        room_offset = navbar_item[1].string[:-1]
        room_offset = 1 if room_offset == "" else int(room_offset) // 10
        return room_offset


class Room:
    """
    Room Object
     * extracts listing info from the listing's page (not the search results page)
     * calculates commute times to workplace

    Contains:
        url
        title
        description
        features (minimum term, maximum term, deposit, bills included, furnishings, parking, garage, garden
                  balcony, disabled access, living room, broadband, housemates. total rooms, ages, smoker, pets,
                  language, occupation, gender, couples ok, smoking ok, pets ok, references, min age, max age)
        gps_location
        commute distance to workplace (by public transport and cycling)

    """

    logger = DwellistLogger.get_logger()

    def __init__(self, room_soup, domain):
        # Get listing page
        self.url = str(domain + room_soup.find("a")["href"])
        self.id = int(self.url.split("flatshare_id=")[1].split("&")[0])
        room_soup = BeautifulSoup(requests.get(self.url).content, "lxml")
        # Populate basics from the search results page
        try:
            header = room_soup.find("div", {"id": "listing_heading"})
            self.title = str(header.h1.text.strip()) if header.h1 else None
        except AttributeError:
            self.logger.error("Error parsing listing page - probably not live")
            return
        self.desc = str(
            room_soup.find("p", {"class": "detaildesc"})
            .text.strip()
            .replace("\r\n", " ")
        )

        key_features = self._get_key_features(room_soup)
        [setattr(self, feature, key_features[feature]) for feature in key_features]

        pm_prices = self._get_all_room_prices_pm(room_soup)
        for i, room in enumerate(pm_prices):
            price, type = int(str(room["price"]).replace(",", "")), room["type"]
            setattr(self, f"room_{i+1}_price", price)
            setattr(self, f"room_{i+1}_type", type)

        self.location_coords = self._get_location_coords(room_soup)

        features = self._get_features(room_soup)

        for header in features:
            value = features[header]
            setattr(self, header, value)

        # Todays date
        self.date_scraped = datetime.datetime.now().strftime("%d-%m-%Y")

    def __str__(self):
        return str(self.__dict__)

    def _get_all_room_prices_pm(self, room_soup):
        rooms = []
        price_list = []
        theclass = "room-list"
        room_price_lists = room_soup.find("ul", class_="room-list")
        try:
            if room_price_lists is None:
                theclass = "feature--price-whole-property"
                room_price_lists = room_soup.find(
                    "section", class_="feature--price-whole-property"
                )
                whole_property_price = room_price_lists.find(
                    "h3", class_="feature__heading"
                )
                if whole_property_price:
                    price_text = whole_property_price.text
                    # Extracting the price from the text using string manipulation
                    price = price_text.split("£")[1].split()[0]
                    rooms.append({"price": price, "type": "Whole Property"})
                    return rooms
                raise AttributeError("No room price found")
            else:
                price_list = room_price_lists.find_all("li")

            for li in price_list:
                # get price from strong class="room-list__price"
                price = li.find("strong", {"class": "room-list__price"}).text.strip()
                price, interval = price.split(" ")
                price = price.replace("£", "")
                if interval == "pw":
                    price = int(int(price.replace(",", "")) * (52 / 12))
                type = li.find("small").text.strip().replace("(", "").replace(")", "")
                rooms.append({"price": price, "type": type})
        except Exception as e:
            # Save room soup to file for debugging
            with open(f"room_debug/room_{self.id}.html", "w", encoding="utf-8") as file:
                file.write(str(room_soup))
            self.logger.error("Error parsing room price: %s", e)
            self.logger.info(self.url)
            self.logger.info(theclass)
        return rooms

    def _get_key_features(self, room_soup):
        feature_list = room_soup.find("ul", class_="key-features")
        features = {
            "type": None,
            "area": None,
            "postcode": None,
            "nearest_station": None,
        }
        for i, li in enumerate(feature_list.find_all("li")):
            # check if there is a sublist, and if so only take the first element
            text = li.text.strip().replace("\n", "").strip()
            text = " ".join(text.split())
            if i == 2:
                text = text.split(" ")[0]
            elif i == 3:
                text = text.split("\n")[0]

            features[list(features.keys())[i]] = text
        return features

    def _get_features(self, room_soup):
        feature_lists = room_soup.findAll("dl", class_="feature-list")
        features = {}
        for feature_list in feature_lists:
            for dt, dd in zip(feature_list.find_all("dt"), feature_list.find_all("dd")):
                key = dt.text.replace("\n", "").replace("#", "").strip().lower()
                # Replace spaces, dashes, slashes, parentheses, quotes, colons, periods, commas, and ampersands with underscores
                key = key.translate(str.maketrans(" -/()':.,&?", "___________"))
                # Replace multiple underscores with a single underscore
                key = "_".join(key.split("_")).strip("_")
                features[key] = dd.text.strip()

        main_image = self._get_main_image(room_soup)
        if main_image is not None:
            features["main_image"] = main_image

            images = room_soup.find("ul", class_="additional_photo_list--has-photos")
            for image_no, image_link in enumerate(images.find_all("a")):
                # Get image from img src
                link = image_link["href"]
                # Ensure image link is prefixed with https:
                link = link if link.startswith("https:") else f"https:{link}"
                features[f"image_{image_no}"] = link

        # features["postcode"].replace("Area info", "")
        return features

    def _get_main_image(self, room_soup):
        try:
            main_image_container = room_soup.find("dl", class_="landscape")
            if main_image_container:
                main_image = main_image_container.find("img")["src"]
                main_image = (
                    main_image
                    if main_image.startswith("https:")
                    else f"https:{main_image}"
                )
                return main_image
            else:
                return None  # Return None if main_image_container is not found
        except (AttributeError, KeyError):
            return None  # Handle exceptions and return None in case of errors

    def _get_location_coords(self, room_soup):
        script_text = room_soup.head.findAll("script")
        for script in script_text:
            script_text = script.text
            if "_sr.page" in script_text:
                try:
                    location_idx = script_text.find("location")
                    if location_idx == -1:
                        continue
                    location = script_text[location_idx : location_idx + 100]
                    location = location.split("{")[1].split("}")[0]
                    location = location.split(",")[:-1]
                    location = [
                        float(l.split(":")[1].strip().replace('"', ""))
                        for l in location
                    ]
                    # latitude, longitude
                    location = (location[0], location[1])
                except ValueError as e:
                    self.logger.debug("Error parsing location: %s", e)
                    location = None
                except Exception as e:
                    self.logger.debug(self.url)
                    self.logger.info(traceback.format_exc())
                return location


def read_existing_rooms_from_spreadsheet(file_path):
    try:
        df = pd.read_csv(file_path)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        print("Creating new spreadsheet for rooms.")
        df = pd.DataFrame()
    return df


def append_new_rooms_to_spreadsheet(df, new_rooms, file_path):
    new_df = pd.DataFrame([room.__dict__ for room in new_rooms])
    if df is None or df.empty:
        combined_df = new_df
    else:
        combined_df = pd.concat([df, new_df], ignore_index=True)

    # Reorder columns
    def reorder_columns(columns):
        room_columns = [col for col in columns if col.startswith("room_")]
        deposit_columns = [col for col in columns if col.startswith("Deposit")]
        non_room_columns = [
            col for col in columns if (col not in room_columns + deposit_columns)
        ]

        room_and_deposit = [
            room_columns[i * 2 : i * 2 + 2] + [deposit_columns[i]]
            for i in range(len(deposit_columns))
        ]
        # flatten list
        room_and_deposit = [item for sublist in room_and_deposit for item in sublist]

        reordered_columns = []
        for col in non_room_columns:
            reordered_columns.append(col)
            if col.startswith("Maximum term"):
                reordered_columns.extend(room_and_deposit)
        return reordered_columns

    reordered_columns = reorder_columns(combined_df.columns)
    combined_df = combined_df[reordered_columns]

    combined_df.to_csv(file_path, index=False)
