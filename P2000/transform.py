import json
import time
import os
import re
"""
This code use to filter latitude, longitude, postal code and house number and date of P200 messages
The filter operation is performed to 'parsed_w_precise_coords.json/precise_w_2022-2016_new.json'
"""

def load_data(data):
    file = open(data)
    data = json.load(file)
    return data

def filter(data):
    extracted_data = []
    for obj in data:
        # print(obj)
        # create a new dictionary to store the extracted data for each object
        address = obj["address"]
        number = re.search(r'\d{1,4}', address)
        formatted_address = obj["google_results"][0]['formatted_address']
        zipcode = re.search(r'\d{4}\s?[A-Z]{2}', formatted_address)
        
        if zipcode is not None and number is not None:
            zipcode = zipcode.group()
            zipcode = zipcode.replace(" ", "")
            number = number.group()
        else:
            continue
        if len(number) == 0:
            continue
        new_obj = {}
        new_obj["date"] = obj["date"]
        new_obj["zipcode"] = zipcode
        new_obj["housenumber"] = number
        new_obj["lat"] = obj["latitude"]
        new_obj["lng"] = obj["longitude"]

        # add the new dictionary to the list
        extracted_data.append(new_obj)
    
    with open("parsed_w_transform_precise_coords_complete.json", "w") as file:
        json.dump(extracted_data, file, indent=4)
        print("done!")
    
def main():
    current_path = os.getcwd()
    data = load_data(f"{current_path}/precise_w_2022-2016_new.json")
    filter(data)

if __name__ == '__main__':
    main()