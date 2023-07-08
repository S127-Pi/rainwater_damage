# Code from Thijs Simons is used: https://github.com/SimonsThijs/wateroverlast
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from datetime import datetime, timedelta

import time
import json

# The URL for API calls is the following: it ends with a timestamp and will return a number of p2000 which are the closest but lower than the given time
url = "http://api.alarmfase1.nl/3.2/calls/fire.json?&end={}"

"""
Value error: 2022-05-02 19:00:49
2020-09-04 20:26:23
2020-09-04 15:53:49

"""
strfformat = "%Y-%m-%d %H:%M:%S" # Format of the timestamp which is formatted into the URL
enddate = datetime(year=2016, month=3, day=14, hour=0, minute=0, second=0)
# prevdate = datetime.now()
prevdate = datetime.strptime("2022-12-31 23:59:59", strfformat)

out_file = open("final2.json", "w")

list_wateroverlast_calls = [] # List of p2000 calls which contain the word 'wateroverlast'

while prevdate > enddate:
    # A session is made so it possible to give a number of max retries for an API call (to avoid errored API calls)
    session = requests.Session()
    retry = Retry(connect=5, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    data = session.get(url.format(prevdate.strftime(strfformat)))
    
    try:
        calls = data.json()["calls"]
    except ValueError: # This happens when the return value of the API call cannot be formatted into a json object 
        prevdate = prevdate - timedelta(hours=5)
        continue

    for c in calls:
        print(c)
        if 'wateroverlast' in c['message'].lower():
            print(c)
            list_wateroverlast_calls.append(c) # Only calls which are possibly relevant are saved 
    # try:
    #     prevdate = datetime.strptime(calls[-1]["date"], strfformat)
    # except ValueError: # This happens when the return value of the API date call is wrongly formatted
    #     print(calls)
    #     print("wrongly formatted")
    #     print(f"ValueError!")
    #     break
    
    # date_found = False
    # for call in reversed(calls):
    #     try:
    #         api_date_str = call["date"]
    #         print(api_date_str)
    #         # Parse the date string using a format string that handles optional fields
    #         api_date = datetime.strptime(api_date_str, "[%Y][%-Y][%m][%-m][%d][%-d] %H:%M:%S")
    #         # Create a new datetime object with the desired format
    #         prevdate = api_date.strftime("%Y-%m-%d %H:%M:%S")
    #         date_found = True
    #         break
    #     except ValueError:
    #         pass
    # if not date_found:
    #     print("Error: Could not find a valid date in calls.")

    # if not date_found:
    #     print("Error: Could not find a valid date in calls.")

    
    prevdate = datetime.strptime(calls[-1]["date"], strfformat) # This becomes the timestamp of the earliest p2000 call. Note: this does not have to be a call which is a 'wateroverlast' call. 
    
    print(f"{prevdate}: Data Saved")
    time.sleep(0.1)
    print("Fetching another data")

data = {"data": list_wateroverlast_calls}

json.dump(data, out_file, indent=6)
out_file.close()
