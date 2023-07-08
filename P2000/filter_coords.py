import json

"""
Get only home objects
"""

# Load JSON data
with open('coord.json', 'r') as file:
    data = json.load(file)

# Filter elements based on "types"
filtered_data = [element for element in data if element['google_results'][0]['types'] != ["route"]]


with open('filtered_coords_new.json', 'w') as file:
    json.dump(filtered_data, file, indent= 4)