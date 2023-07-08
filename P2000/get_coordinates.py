# Code from Thijs Simons is used: https://github.com/SimonsThijs/wateroverlast
from maps_api import MapsApi

import os
import json


def load_data(file):
    with open(file, 'r') as file:
        data = json.load(file)
        return data


def print_data():
    data = load_data('parsed.json')
    for d in data:
        if len(d['address'].split(' ')) <= 1:
            print(d['message'], "-----", d['address'], "----- ")


def print_json(data):
    to_print = ''
    to_print += '['
    for d in data:
        to_print += json.dumps(d) + ",\n"

    to_print = to_print[0:-2]
    to_print += ']\n'
    print(to_print)


def main():
    dire = os.getcwd()
    key = os.environ.get["API key"]
    api = MapsApi(key=key)
    data = load_data(f'{dire}/P2000/patched.json')['data']
    data_coord = []
    amount = len(data)
    for idx, d in enumerate(data):
        print(f"{idx} of {amount}")                     
        google_results = None
        try:
            google_results = api.get_coordinate(d['address'] + ", Netherlands")
        except Exception as e:
            try:
                google_results = api.get_coordinate(
                    d['address'] + ", Netherlands")
            except Exception as e:
                try:
                    google_results = api.get_coordinate(
                        d['address'] + ", Netherlands")
                except Exception as e:
                    pass

        if google_results and google_results['status'] == 'OK':
            d['google_results'] = google_results['results']
            data_coord.append(d)

        # else:
        #     print("ERROR")
        #     print(json.dumps(d) + ",")
    out_file = open("coord.json", "w")
    json.dump(data_coord, out_file, indent=6)
    out_file.close()           
    


if __name__ == '__main__':
    # print_data()
    main()
