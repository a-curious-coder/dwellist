import datetime
from dwellist.logger import DwellistLogger
import traceback
from bs4 import BeautifulSoup as Soup


class Listing:
    """
    Listing Object
     * gets info from the room listing page

    Gets:
        url
        title
        description
        features (minimum term, maximum term, deposit, bills included, furnishings, parking, garage, garden
                  balcony, disabled access, living room, broadband, housemates. total rooms, ages, smoker, pets,
                  language, occupation, gender, couples ok, smoking ok, pets ok, references, min age, max age)
        gps_location
        images
        room prices
        date_scraped
    """

    logger = DwellistLogger.get_logger()

    def __init__(self, listing, domain):
        self.id = -1
        try:
            self.id = listing.prettify().split("flatshare_id=")[1].split("&")[0]
        except (KeyError, ValueError, IndexError) as e:
            self.logger.error("Error parsing room id: %s", e)

        self.available = True
        if "Sorry, this room is no longer available" in listing.prettify():
            self.available = False

        self.url = domain + self.id
        self.title = "Unknown Title"
        try:
            title = listing.find("div", {"id": "listing_heading"})
            self.title = str(title.h1.text.strip()) if title.h1 else None
        except AttributeError:
            self.logger.error("Could not extract header page title")

        self.description = (
            listing.find("p", {"class": "detaildesc"}).text.strip().replace("\r\n", " ")
        )

        key_features = self._get_key_features(listing)
        [setattr(self, feature, key_features[feature]) for feature in key_features]

        room_prices_per_month = self._get_room_prices_pm(listing)
        for i, room_price_info in enumerate(room_prices_per_month):
            price, type = (
                room_price_info["price"],
                room_price_info["type"],
            )
            setattr(self, f"room_{i+1}_price", price)
            setattr(self, f"room_{i+1}_type", type)

        self.location_coords = self._get_location_coords(listing)
        self.latitude = self.location_coords[0] if self.location_coords else None
        self.longitude = self.location_coords[1] if self.location_coords else None

        features = self._get_features(listing)

        for header in features:
            value = features[header]
            setattr(self, header, value)

        # Todays date
        self.date_scraped = datetime.datetime.now().strftime("%d-%m-%Y")

    def __str__(self):
        return str(self.__dict__)

    def _get_room_prices_pm(self, listing: Soup) -> list:
        room_prices = []
        price_list = []
        room_price_lists = listing.find("ul", class_="room-list")
        try:
            if room_price_lists is None:
                room_price_lists = listing.find(
                    "section", class_="feature--price-whole-property"
                )
                whole_property_price = room_price_lists.find(
                    "h3", class_="feature__heading"
                )
                if whole_property_price:
                    price_text = whole_property_price.text
                    # Extracting the price from the text using string manipulation
                    price = price_text.split("£")[1].split()[0]
                    room_prices.append({"price": price, "type": "Whole Property"})
                    return room_prices
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
                room_prices.append({"price": price, "type": type})
        except Exception as e:
            # Save room soup to file for debugging
            with open(f"room_{self.id}.html", "w", encoding="utf-8") as file:
                file.write(str(listing))
            self.logger.error("Error parsing room price: %s", e)
            self.logger.info(self.url)
        return room_prices

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

            # roo
            images = room_soup.find(
                "div",
                class_="photo-gallery__thumbnails photo-gallery__thumbnails--has-photos",
            )
            for image_no, image_link in enumerate(images.find_all("a")):
                # Get image from img src
                link = image_link["href"]
                # Ensure image link is prefixed with https:
                link = link if link.startswith("https:") else f"https:{link}"
                features[f"image_{image_no+1}"] = link

        # features["postcode"].replace("Area info", "")
        return features

    def _get_main_image(self, room_soup):
        try:
            main_image_container = room_soup.find(
                "dl", class_="photo-gallery__main-image-wrapper landscape"
            )
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
