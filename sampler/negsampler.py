import json
import os 
import requests
import re
import random
"""
positive cases sampler for object level
For more information about several end-points: https://www.pdok.nl/how-to-faq1
"""
class Sampler():
    def __init__(self):
        self.dire = os.getcwd()
    
    def add_negative_object(self, postcode:str, number:int, n_sample:int):
        
        url = f"https://geodata.nationaalgeoregister.nl/locatieserver/v3/free?q={postcode}&bfq=+type:postcode"
        params = {
                "rows": 100,  
                "start": 0  
                }
        response = requests.get(url, params=params)
        houses = []
        try:
            if response.status_code == 200:
                result = response.json()
                houses.extend(result["response"]["docs"])
                houses = houses [1:]
                n_houses = len(houses)

                coordinates = [(item['centroide_ll'].replace('POINT(', '').replace(')', '').split()[::-1], item['huisnummer']) for item in houses]
                sample_coordinates = [(float(coord[0][0]), float(coord[0][1]), int(coord[1])) for coord in coordinates]

                # We do not want the same house as the positive case
                sample_coordinates = [elem for elem in sample_coordinates if number not in elem]

                # Obtain only coordinates
                sample_coordinates = [(float(x), float(y), number) for x, y, number in sample_coordinates]
                # print(len(sample_coordinates))

                # check for 4 negative samples
                if len(sample_coordinates) < n_sample:
                    return None

                return sample_coordinates

        except Exception as e:
            print(e)
            return None
    
    def add_positive_district(self, postcode:str, coordinates:tuple, n_sample:int):
        
        url = f"https://geodata.nationaalgeoregister.nl/locatieserver/v3/free?q={postcode}&bfq=+type:postcode"
        params = {
                "rows": 100,  
                "start": 0  
                }
        response = requests.get(url, params=params)
        houses = []
        try:
            if response.status_code == 200:
                result = response.json()
                houses.extend(result["response"]["docs"])
                houses = houses [1:]
                n_houses = len(houses)

                coordinates = [(item['centroide_ll'].replace('POINT(', '').replace(')', '').split()[::-1], item['postcode']) for item in houses]
                sample_coordinates = [(float(coord[0][0]), float(coord[0][1]), coord[1]) for coord in coordinates]

                sample_coordinates = [elem for elem in sample_coordinates if coordinates not in elem[:2]]
                # Obtain only coordinates
                sample_coordinates = [(float(x), float(y), postcode) for x, y, postcode in sample_coordinates]

                # check for 4 negative samples
                if len(sample_coordinates) < n_sample:
                    return None

                return sample_coordinates

        except Exception as e:
            print(e)
            return None
    
    def add_negative_subdistrict(self, origin_postcode:str, n_sample:int):
        """_summary_

        Args:
            postcode (str): postal code 6
            n_sample (int): desired amount of samples to be returned

        Returns:
            _type_: list
        """
        postcode = origin_postcode[:-1]
        url = f"https://geodata.nationaalgeoregister.nl/locatieserver/v3/suggest?q={postcode}&bfq=+type:postcode"
        params = {
                "rows": 100,  
                "start": 0  
                }
        response = requests.get(url, params=params)
        result = response.json()
        addresses = []
        addresses.extend(result["response"]["docs"])
        addresses = [item['weergavenaam'] for item in addresses]
        postal_codes = []
        
        #extract postal codes from addresses
        for address in addresses:
            postal_code = re.findall(r'\b\d{4}\w{2}\b', address)
            postal_codes.extend(postal_code)
        if origin_postcode in postal_codes:
            postal_codes.remove(origin_postcode)
        #Choose random postal code 6
        postcode6 = random.choice(postal_codes)
        
        
        #Choose n random houses
        url = f"https://geodata.nationaalgeoregister.nl/locatieserver/v3/free?q={postcode6}&bfq=+type:postcode"
        response = requests.get(url, params=params)
        houses = []
        try:
            if response.status_code == 200:
                result = response.json()
                houses.extend(result["response"]["docs"])
                houses = houses[1:]
                n_houses = len(houses)

                coordinates = [(item['centroide_ll'].replace('POINT(', '').replace(')', '').split()[::-1], item['postcode']) for item in houses]
                sample_coordinates = [(float(coord[0][0]), float(coord[0][1]), coord[1]) for coord in coordinates]


                # Obtain only coordinates
                sample_coordinates = [(float(x), float(y), postcode) for x, y, postcode in sample_coordinates]

                # check for 5 negative samples
                if len(sample_coordinates) < n_sample:
                    return None

                return sample_coordinates

        except Exception as e:
            print(e)
            return None
    
    
if __name__ == "__main__":
    SP = Sampler()
    # print(SP.add_negative_object("2283SM", number=214, n_sample=2))
    print(SP.add_negative_subdistrict("2287BD", 5))