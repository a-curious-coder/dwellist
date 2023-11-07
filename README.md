# <img src="dark-minimal-house.png" width="20" height="25" /> Dwellist
Feel free to message me on discord @curious_coder if you want to contribute in making this project better.

This project collates property data from Spareroom UK based on the filter values in the `config.json`. 
The data is saved to a csv file which the Flask web app reads and displays via markers on a Leaflet JS map. You can filter the markers further via the filter form on the web app.

![image](https://amazingarchitecture.com/storage/3659/talos_ai_generated_house_gg_loop.jpg)

<!-- TODO: Update the following section -->
# Usage
1. Create a virtual environment
2. Install requirements
3. Run the script with `python main.py`

# Data information
## Data Table
| Filter                  | Example Value      | Data Type          |
|-------------------------|--------------------|--------------------|
| Filename                | listings.csv | String          |
| Search Term             | London             | String             |
| Rooms to Scrape         | 1000               | Integer            |
| Bills Included          | Yes                | String (Boolean)   |
| Minimum Rent            | £700 per month     | String (Currency)  |
| Maximum Rent            | £1100 per month    | String (Currency)  |
| Show 1-Bed Properties   | Yes                | String (Boolean)   |
| Show Rooms              | Yes                | String (Boolean)   |
| Distance from Max Mile  | 1 mile             | Integer            |
| Rent Period             | Per calendar month | String             |
| Days Available          | 7+ days a week     | String             |
| Couples                 | No                 | String (Boolean)   |
| Days of Week Available  | Monday-Friday      | String             |
| Disabled Access         | Yes                | String (Boolean)   |
| Ensuite                 | No                 | String (Boolean)   |
| Fees Apply              | No                 | String (Boolean)   |
| Gayshare                | Yes                | String (Boolean)   |
| Gender Filter           | Female             | String             |
| Keyword                 | Spacious           | String             |
| Landlord                | John Doe           | String             |
| Living Room             | Yes                | String (Boolean)   |
| Maximum Age Requirement | 35                 | Integer            |
| Maximum Suitable Age    | 40                 | Integer            |
| Maximum Beds            | 3                  | Integer            |
| Maximum Other Areas     | 2                  | Integer            |
| Maximum Term            | 12 months          | Integer            |
| Minimum Age Requirement | 25                 | Integer            |
| Minimum Suitable Age    | 30                 | Integer            |
| Minimum Beds            | 2                  | Integer            |
| Minimum Term            | 6 months           | Integer            |
| Number of Rooms         | 4                  | Integer            |
| Parking                 | Yes                | String (Boolean)   |
| Pets Requirement        | Dogs               | String             |
| Photos Only             | Yes                | String (Boolean)   |
| Posted By               | Agent              | String             |
| Furnished               | Yes                | String (Boolean)   |
| Rooms For               | Students           | String             |
| Share Type              | Flatmates          | String             |
| Short Lets Considered   | Yes                | String (Boolean)   |
| Buddyup Properties      | No                 | String (Boolean)   |
| Smoking                 | No                 | String (Boolean)   |
| Vegetarians             | Yes                | String (Boolean)   |

## Fields
Below, I've included the settings and filters with example values
```json
{
  "filename": "spareroom_listing.csv",
  "search_term": "London",
  "rooms_to_scrape": 1000,
  "bills_inc": true,
  "min_rent": 700,
  "max_rent": 1100,
  "showme_1beds": true,
  "showme_rooms": true,
  "miles_from_max": 1,
  "per": "pcm",
  "available_from": "",
  "available_search": "",
  "couples": false,
  "days_of_wk_available": "Monday-Friday",
  "disabled_access": true,
  "ensuite": false,
  "fees_apply": false,
  "gayshare": true,
  "genderfilter": "Female",
  "keyword": "Spacious",
  "landlord": "John Doe",
  "living_room": true,
  "max_age_req": 35,
  "max_suitable_age": 40,
  "max_beds": 3,
  "max_other_areas": 2,
  "max_term": 12,
  "min_age_req": 25,
  "min_suitable_age": 30,
  "min_beds": 2,
  "min_term": 6,
  "no_of_rooms": 4,
  "parking": true,
  "pets_req": "Dogs",
  "photoadsonly": true,
  "posted_by": "Agent",
  "room_types": "Double",
  "furnished": true,
  "rooms_for": "Students",
  "share_type": "Flatmates",
  "short_lets_considered": true,
  "showme_buddyup_properties": false,
  "smoking": false,
  "vegetarians": true
}
```

## Credits
The barebones of the scraper were stolen and reformed from https://github.com/afspies/spareroom-scraper (Thanks dude)