import json
import os

"""
Merge obtained p2000 from 2016-2021 data with new json data from 2021-2022
"""
def load_data(data):
    file = open(data)
    data = json.load(file)
    return data


def merge_data(new_data, old_data):
    merged_data = new_data + old_data
    merged_data = sorted(merged_data, key=lambda x: x['date'])
    with open("precise_w_2022-2016_new.json", "w") as file:
        json.dump(merged_data, file, indent=4)

def main():
    current_path = os.getcwd()
    new_data = load_data(f"{current_path}/filtered_coords_new.json")
    old_data = load_data(f"{current_path}/parsed_w_precise_coords.json")
    merge_data(new_data, old_data)
    
if __name__ == "__main__":
    main()