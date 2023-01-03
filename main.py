import requests
import json
import os

"""
CHF = swiss franc
CAD = canadian dollar

we use CHF bc it is very stable --> we need stable to compare over long periods of time! 

######
Every month -- the intiial value will be reset! + stored
- every month store the CHF:CAD exchange rate
- allow user to input a date -- returns the vallue of CAD relative to CHF on that date --> used to compare value of CAD as time passes and how much it changes by
- etc

link: https://www.cmcmarkets.com/en/learn-forex/16-strongest-currencies-in-the-world

we only want CHF-CAD for now --> so this app looks for the USD to CAD exchange rate across every day per month???
"""

# data for CAD vs CHF == across a few days / month
# store the conversion ratios -- calculate value of cad for each day
KEY = "CHFCAD"
LOADED_DATA = {}

# ---------------------------------------- #
# extracting / parsing data

def extract_data_from_json(fname, key):
    """Extract data from a json file"""
    with open(fname, 'r') as file:
        data = json.load(file)
    return extract_data_from_dict(data, key)

def extract_data_from_dict(data, key):
    """Extract data from a dictionary"""
    return data["quotes"][key]

def request_data_for_date(year: int, month: int, day: int) -> dict:
    """Request data for a specific date"""
    yy = str(year)[2:]
    mm = str(month).zfill(2)
    dd = str(day).zfill(2)
    date = f"{yy}-{mm}-{dd}"
    # check if date data is already collected
    if check_data_cached(year, month, day):
        return LOADED_DATA[year][month][day]
    # if not cached, check if exists within data folder
    # print(os.listdir("data"))
    # print(f"{date}.json")
    # print(f"{date}.json" in os.listdir("data"))
    if f"{date}.json" in os.listdir("data"):
        return collect_data_for_one_day(year, month, day)
    # request data
    # TODO - MAKE SURE 
    # 1. configure how to request specific money types
    # print("THERE IS STUFF TO DO HERE ", __file__)
    date2 = f"{year}-{mm}-{dd}"
    # source = "CHF"
    url = f"https://api.apilayer.com/currency_data/historical?date={date2}&source=CHF&currencies=CAD"
    payload = {}
    headers = {"apikey": "BksbdsXpfRfB35Qbs30OyOC3vUQK2L7l"}
    response = requests.request("GET", url, headers=headers, data=payload)
    status_code = response.status_code
    result = response.text
    # save data
    save_dict_to_json(result, f"data/{date}.json")
    return json.loads(result)

def save_dict_to_json(data, fname):
    """Save a dictionary to a json file"""
    with open(fname, 'w') as file:
        if type(data) == str:
            data = json.loads(data)
        json.dump(data, file)

def parse_data_ratio(date1: str, date2: str, ratio: float):
    """Parse the data ratio into a string"""
    return f"Convert: {date1:^10} to {date2:^10} | Ratio: {(round(ratio*10000)/10000 if ratio else None)}"

def parse_date_data(year, month, day):
    """Parse the date into a string"""
    return f"{str(year)[2:]}-{str(month).zfill(2)}-{str(day).zfill(2)}"

# ---------------------------------------- #
# caching data

def cache_data(year, month, day, ratio):
    """Cache the data within global storage"""
    if not year in LOADED_DATA:
        LOADED_DATA[year] = {}
    if not month in LOADED_DATA[year]:
        LOADED_DATA[year][month] = {}
    LOADED_DATA[year][month][day] = ratio

def collect_data_for_one_day(year, month, day, cache=True, load_if_not: bool = False):
    """collect data for one day and returns it"""
    fname = os.path.join("data", f"{str(year)[2:]}-{'0' if len(str(month)) == 1 else ''}{month}-{'0' if len(str(day)) == 1 else ''}{day}.json")
    if not os.path.exists(fname): 
        # attempt loading data by pinging
        dict_data = request_data_for_date(year, month, day)
        ratio = extract_data_from_dict(dict_data, KEY)
    else:
        ratio = extract_data_from_json(fname, KEY)
    # cache if required
    if cache:
        cache_data(year, month, day, ratio)
    return extract_data_from_json(fname, KEY)

def collect_data_for_one_month(year, month, load_if_not:bool = False) -> dict:
    """Collects data for one month and returns it as a dict"""
    data = {}
    for i in range(1, 32):
        data_value = collect_data_for_one_day(year, month, i, load_if_not=load_if_not)
        data[i] = data_value
    return data

def collect_data_for_one_year(year, load_if_not: bool = False) -> dict:
    """Collects data for one year and returns it as a dict"""
    data = {}
    for i in range(1, 13):
        data_value = collect_data_for_one_month(year, i, load_if_not=load_if_not)
        data[i] = data_value
    return data

def check_data_cached(year, month, day):
    """Checks if data is cached"""
    return year in LOADED_DATA and month in LOADED_DATA[year] and day in LOADED_DATA[year][month]

# ---------------------------------------- #
# conversion ratio

# assume first day of month = value of 1 CAD in CHF
# assuming CHF is const:: CAD1 / CHF1 = CAD2 / CHF2
def calculate_cad_growth(val1: float, val2: float):
    """Calculate the growth of CAD | past = val1, present = val2"""
    return val1 / val2

def calculate_conversion_ratio(year, month, day) -> float:
    """Calculate the conversion ratio between two dates"""
    # find the first day of the month -- or the lowest day num
    base = min(LOADED_DATA[year][month].items(), key=lambda x: x[0])
    day1, ratio1 = base
    # check if data exists for the day given!
    if not check_data_cached(year, month, day):
        # try loading data!
        collect_data_for_one_day(year, month, day)
        if not check_data_cached(year, month, day):
            # if still not cached -- return None
            return None
    # find the ratio for the day
    ratio2 = LOADED_DATA[int(year)][int(month)][int(day)]
    result = calculate_cad_growth(ratio1, ratio2)
    return result

def calculate_conversion_ratio_and_parse(year, month, day):
    """Calculate the conversion ratio and parse it into a string"""
    return parse_data_ratio(parse_date_data(year, month, 1), parse_date_data(year, month, day), calculate_conversion_ratio(year, month, day))

# ---------------------------------------- #
# testing

print(collect_data_for_one_month(2022, 12, load_if_not=True))
# print(LOADED_DATA)

# print(request_data_for_date(2023, 1, 2))

for i in range(1, 32):
    print(calculate_conversion_ratio_and_parse(2022, 12, i))

# TODO - make console application!!!
#       - OR, make webapp

