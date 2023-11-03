# Dwellist
Feel free to message me on discord @ curious_coder if you want to contribute in making this project better.

Collates and displays Spareroom listings according to config.json. 
Outputs a .csv and can be re-run daily.
Unsure of usage limits atm.

The barebones of the scraper were stolen and bastardised from https://github.com/afspies/spareroom-scraper (Thanks dude)

## Filtered google sheet
![image](https://user-images.githubusercontent.com/14139469/235493682-db45832a-e911-4813-bbc6-bf55341f4181.png)

<!-- TODO: Update the following section -->
# Usage
1. Create a file called config.json in the same directory as main.py
2. Below is an example config.json. The fields are self explanatory.
```json
{
    "SEARCH_URL": "/search.pl?nmsq_mode=normal&action=search&max_per_page=&flatshare_type=offered&search=%search_term%&min_rent=%MIN_RENT_GBP%&max_rent=%MAX_RENT_GBP%&per=pw&available_search=N&day_avail=%AVAILABILITY_FROM_DAY%&mon_avail=%AVAILABILITY_FROM_MONTH%&year_avail=%AVAILABILITY_FROM_YEAR%&min_term=0&max_term=0&radius=2&days_of_wk_available=7+days+a+week&showme_rooms=Y",

    "filename": "spareroom_listings.csv",
    "search_term": "<search_term>",
    "rooms_to_scrape": 300,
    "AVAILABILITY_FROM_DAY": 1,
    "AVAILABILITY_FROM_MONTH": 11,
    "AVAILABILITY_FROM_YEAR": 2023,
    // The below fields are prices per week
    "MIN_RENT_GBP": 175, 
    "MAX_RENT_GBP": 225,
}
```
3. Run the script with `python main.py`
4. Open results using SandDance VSCode extension or Google Sheets

# Data information
## Fields
`url,id,title,desc,Type,area,Postcode,Nearest station,location_coords,cycle_time,transit_time,Available,Minimum term,Maximum term,room_0_price,room_0_type,Deposit,room_1_price,room_1_type,Deposit(room 1),room_2_price,room_2_type,Deposit(room 2),Bills included?,Furnishings,Parking,Garage,Garden/terrace,Balcony/patio,Disabled access,Living room,Broadband included,Flatmates,Total rooms,Age,Smoker?,Any pets?,Language,Nationality,Occupation,Gender,Couples ok?,Smoking ok?,Pets ok?,References?,Min age,Ages,Interests,Max age,Housemates,Orientation,University,Vegetarian,date_scraped`


