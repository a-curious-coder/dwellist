""" This module is responsible for constructing the search URL based on the config file. """
from datetime import datetime


class SearchConstructor:
    """This class is responsible for constructing the search URL based on the config file."""

    BASE_URL = "https://www.spareroom.co.uk/flatshare/search.pl?nmsq_mode=normal&action=search&flatshare_type=offered"

    def __init__(self, config):
        self.config = config
        self.search_url = self._construct_search_url()

    def _construct_search_url(self):
        search_url = self.BASE_URL
        # Configure todays date for the available_from filter
        today = datetime.today().strftime("%Y-%m-%d")
        filters = {
            "available_from": self.config.get("available_from", today),
            "available_search": self.config.get("available_search", ""),
            "bills_inc": self.config.get("bills_inc", "Y"),
            "couples": self.config.get("couples", ""),
            "days_of_wk_available": self.config.get(
                "days_of_wk_available", "7+days+a+week"
            ),
            "disabled_access": self.config.get("disabled_access", ""),
            "ensuite": self.config.get("ensuite", "Y"),
            "fees_apply": self.config.get("fees_apply", ""),
            "gayshare": self.config.get("gayshare", "N"),
            "genderfilter": self.config.get("genderfilter", ""),
            "keyword": self.config.get("keyword", ""),
            "landlord": self.config.get("landlord", ""),
            "living_room": self.config.get("living_room", ""),
            "max_age_req": self.config.get("max_age_req", ""),
            "max_suitable_age": self.config.get("max_suitable_age", ""),
            "max_beds": self.config.get("max_beds", ""),
            "max_other_areas": self.config.get("max_other_areas", ""),
            "max_rent": self.config.get("max_rent", ""),
            "max_term": self.config.get("max_term", ""),
            "min_age_req": self.config.get("min_age_req", ""),
            "min_suitable_age": self.config.get("min_suitable_age", ""),
            "min_beds": self.config.get("min_beds", 0),
            "min_rent": self.config.get("min_rent", 0),
            "min_term": self.config.get("min_term", 0),
            "miles_from_max": self.config.get("miles_from_max", 0),
            "no_of_rooms": self.config.get("no_of_rooms", ""),
            "parking": self.config.get("parking", ""),
            "per": self.config.get("per", ""),
            "pets_req": self.config.get("pets_req", ""),
            "photoadsonly": self.config.get("photoadsonly", ""),
            "posted_by": self.config.get("posted_by", ""),
            "room_types": self.config.get("room_types", ""),
            "furnished": self.config.get("furnished", ""),
            "rooms_for": self.config.get("rooms_for", ""),
            "search": self.config.get("search_term", ""),
            "share_type": self.config.get("share_type", ""),
            "short_lets_considered": self.config.get("short_lets_considered", ""),
            "showme_1beds": self.config.get("showme_1beds", ""),
            "showme_buddyup_properties": self.config.get(
                "showme_buddyup_properties", ""
            ),
            "showme_rooms": self.config.get("showme_rooms", ""),
            "smoking": self.config.get("smoking", ""),
            "vegetarians": self.config.get("vegetarians", ""),
        }

        for key, value in filters.items():
            if value != "":
                search_url += f"&{key}={value}"

        return search_url

    def get_search_url(self):
        """Returns the search URL"""
        return self.search_url
