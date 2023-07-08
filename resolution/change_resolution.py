import sys
import os 
# setting path
sys.path.append(os.getcwd())

import pandas as pd
import json
import requests
import random
import time
from postcode_finder import find_all_postcode6, find_random_housenumber
from BAG import rdconverter
import re

def search_postcode_in_description(description):
    try:
        # Pattern to match the postal code
        pattern = r'\b\d{4}[A-Z]{2}\b'

        # Extract the postal code using re.search
        match = re.search(pattern, description)
        if match:
            postal_code = match.group()
            return postal_code
        else:
            return None
    except Exception as e:
        return None
        

def get_lat_lng(houses_postcode, headers):
    try:
        rand_pand = random.choice(houses_postcode["_embedded"]["zoekresultaten"])
        zoekidentificatie = rand_pand["identificatie"]
        postcode6 = search_postcode_in_description(rand_pand["omschrijving"])
        response = requests.get(f'https://api.bag.acceptatie.kadaster.nl/lvbag/individuelebevragingen/v2/adressen?zoekresultaatIdentificatie={zoekidentificatie}', headers=headers, timeout=10)
        response = response.json()
        time.sleep(0.2)
        pandidentificatie = response["_embedded"]["adressen"][0]["pandIdentificaties"][0]
        response = requests.get(f'https://api.bag.acceptatie.kadaster.nl/lvbag/individuelebevragingen/v2/verblijfsobjecten?pandIdentificatie={pandidentificatie}', headers=headers, timeout=10)
        time.sleep(0.2)
        coordinates = response.json()["_embedded"]["verblijfsobjecten"][0]["verblijfsobject"]["geometrie"]["punt"]["coordinates"]
        x = coordinates[0]
        y = coordinates[1]
        lat = rdconverter.RD2lat(x, y)
        lng = rdconverter.RD2lng(x, y)
        return((lat, lng), postcode6)
    except Exception as ex:
        print(ex)
        return None 

def get_random_house_sub(postcode, postcodes_df, headers):
    try:
        random_hn = find_random_housenumber(postcodes_df, postcode)
    except Exception as ex:
        return None 
    try:
        houses_postcode = requests.get(f"https://api.bag.acceptatie.kadaster.nl/lvbag/individuelebevragingen/v2/adressen/zoek?zoek={random_hn}&pageSize=100", headers=headers, timeout=10).json()
        time.sleep(0.2)
    except Exception as ex:
        # print(ex)
        try:
            houses_postcode = requests.get(f"https://api.bag.acceptatie.kadaster.nl/lvbag/individuelebevragingen/v2/adressen/zoek?zoek={random_hn}&pageSize=100", headers=headers, timeout=10).json()
            time.sleep(0.2)
        except Exception as ex:
            # print(ex)
            return None
    return houses_postcode
    

def get_random_house(postcode: str, resolution: str, postcodes_df: pd.DataFrame, original_postcode=None, tries=0, ensurance=False):

    # Fill in api key:
    headers = {"X-Api-Key": "l7c5e5789529034d24ad1f1acc25991975",
               "Accept-Crs": "epsg:28992"}

    if resolution == "postcode6":
        postcode_without_spaces = postcode.replace(" ", "")
        houses_postcode = get_random_house_sub(postcode_without_spaces, postcodes_df, headers)
        if houses_postcode is None:
            houses_postcode = get_random_house_sub(postcode_without_spaces, postcodes_df, headers)
        if houses_postcode is None:
            if original_postcode is not None and tries < 2:
                tries += 1 
                return get_random_house(original_postcode, "postcode4", postcodes_df, original_postcode, tries)
            else:
                if tries >= 2:
                    return None 
                try: 
                    houses_postcode = requests.get(f"https://api.bag.acceptatie.kadaster.nl/lvbag/individuelebevragingen/v2/adressen/zoek?zoek={postcode_without_spaces}&pageSize=100", headers=headers, timeout=10).json()
                    embedded = houses_postcode["_embedded"]["zoekresultaten"]
                except Exception as ex:
                    try: 
                        houses_postcode = requests.get(f"https://api.bag.acceptatie.kadaster.nl/lvbag/individuelebevragingen/v2/adressen/zoek?zoek={postcode}&pageSize=100", headers=headers, timeout=10).json()
                        embedded = houses_postcode["_embedded"]["zoekresultaten"]
                    except Exception:                       
                        return None 
            
        output = get_lat_lng(houses_postcode, headers)
        if output is not None:
            return output, postcode
        time.sleep(0.2)
        if original_postcode is not None and tries < 2:
            if original_postcode is not None and tries < 2:
                tries += 1 
                return get_random_house(original_postcode, "postcode4", postcodes_df, original_postcode, tries)
            else:
                try: 
                    output = get_lat_lng(houses_postcode, headers)
                except Exception as ex:
                    return None 

    if resolution == "postcode4":
        if ensurance:
            postcode4 = postcode 
        else:
            postcode4 = postcode[:-2]
        try:
            possible_postcode6 = find_all_postcode6("all_postcode6.txt", postcode4)
        except KeyError:
            try: 
                possible_postcode6 = find_all_postcode6("all_postcode6.txt", postcode)
            except KeyError:
                if original_postcode is not None and tries < 2:
                    tries += 1 
                    return get_random_house(original_postcode, "postcode4", postcodes_df, original_postcode, tries)
                else:
                    return None 
        #obtain complete postal code "2236 -> 2236BD"   
        postcode6 = random.choice(possible_postcode6)
        #Get random house
        return get_random_house(postcode6, "postcode6", postcodes_df, postcode, tries)
    
    if resolution == "postcode5":
        if ensurance:
            postcode5 = postcode 
        else:
            postcode5 = postcode[:-1]
        try:
            possible_postcode6 = find_all_postcode6("postcode5.txt", postcode5)
        except KeyError:
            try: 
                possible_postcode6 = find_all_postcode6("all_postcode6.txt", postcode5)
            except KeyError:
                if original_postcode is not None and tries < 2:
                    tries += 1 
                    return get_random_house(original_postcode, "postcode5", postcodes_df, original_postcode, tries)
                else:
                    return None 
        #obtain complete postal code "2236 -> 2236BD"   
        postcode6 = random.choice(possible_postcode6)
        #Get random house
        return get_random_house(postcode6, "postcode6", postcodes_df, postcode, tries)


def change_resolution(dataset: list, out_file_name: str, resolution):
    print(f"{out_file_name=}")
    data = []
    missing = []
    postcodes_df = pd.read_csv(f"{dire}/resolution/pc6hnr20210801_gwb.csv", sep=";")
    n = len(dataset)
    for i in dataset:
        n -= 1
        if n % 5 == 0:
            print(f"remaining {n}")
        new_item = {}

        if resolution == "postcode4":
            resolution = "postcode4"
        elif resolution == "postcode5":
            resolution = "postcode5"
        else:
            resolution = "postcode6"
        
        output= get_random_house(i['zipcode'], resolution, postcodes_df)
        # print(output)
        if output is None:
            print(i['zipcode'])
            print("Output is None")
            missing.append(i)
            # times += 1
            continue
        try:
            new_item["date"] = i["date"]
            new_item["lat"] = output[0][0][0]
            new_item["lng"] = output[0][0][1]
            zipcode = output = output[0][1]
            if resolution == "postcode4":
                zipcode = zipcode.replace(" ", "")
                zipcode = zipcode
            else:
                zipcode = zipcode.replace(" ", "")
            new_item["zipcode"] = zipcode
            
            print(new_item["zipcode"])
        
        except Exception as e:
            continue
            
        
        #old steps
        data.append(new_item)
        
    out_file = open(f"{out_file_name}missing.json", "w")
    json.dump(missing, out_file, indent=6)
    out_file.close()
    
    out_file = open(f"{out_file_name}.json", "w")
    json.dump(data, out_file, indent=6)
    out_file.close()


def load_data(file):
    print(file)
    with open(file, 'r') as file:
        data = json.load(file)
        return data

if __name__ == "__main__":
    dire = os.getcwd()
    # print(dire)
    dataset = load_data(f'{dire}/resolution/object/parsed_w_transform_precise_coords_complete.json')
    #change_resolution(dataset, "postcode6_number2", "postcode6")
    #change_resolution(dataset, "postcode6_number2", "postcode6")
    # change_resolution(dataset, "postcode6_number3", "postcode6")
    # change_resolution(dataset, "postcode6_number4", "postcode6")
    # change_resolution(dataset, "postcode6_number5", "postcode6")
    

    change_resolution(dataset, "postcode5_number4", "postcode5")
    
    
    #Testing
    # postcodes_df = pd.read_csv(f"{dire}/pc6hnr20210801_gwb.csv", sep=";")
    # house = get_random_house("2287", "postcode4", postcodes_df)
    
    # # Extracting the values into variables
    # (lat, lng), postal_code = house[0]
    # print(postal_code)
    # print(lat)
    # print(get_random_house("2287", "postcode4", postcodes_df))
