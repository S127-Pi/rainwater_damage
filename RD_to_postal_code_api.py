import requests
import rdconverter

"""
This api call is used to obtain postal code based on RD coordinates.

For more information: https://www.pdok.nl/how-to-faq1
"""


def get_postcode(X,Y):
    """Obtain complete postal code with RD coordinates"""
    url = f"https://geodata.nationaalgeoregister.nl/locatieserver/revgeo?X={X}&Y={Y}&type=adres&rows=1&fl=*"
    response = requests.get(url)
    try:
        if response.status_code == 200:
            result = response.json()
            postal_code6 = result["response"]["docs"][0]["postcode"]
            return postal_code6
        
    except Exception as e:
        print(e)
        print(X, Y)
        return None

def get_housenumber(X,Y):
    """Obtain housenumber code with RD coordinates"""
    url = f"https://geodata.nationaalgeoregister.nl/locatieserver/revgeo?X={X}&Y={Y}&type=adres&rows=1&fl=*"
    response = requests.get(url)
    try:
        if response.status_code == 200:
            result = response.json()
            huisnummer = result["response"]["docs"][0]['huisnummer']
            return huisnummer
        
    except Exception as e:
        print(e)
        print(X, Y)
        return None
    
def check_district(X, Y, origin_postcode):
    """Check whether the sample belong the same district as the positve case -> district level"""
        
    url = f"https://geodata.nationaalgeoregister.nl/locatieserver/revgeo?X={X}&Y={Y}&type=adres&rows=1&fl=*"
    response = requests.get(url)
    origin_postcode = int(origin_postcode)
    try:
        if response.status_code == 200:
            result = response.json()
            postal_code = result["response"]["docs"][0]["postcode"]
            postal_code6 = postal_code
            postal_code4 = int(postal_code[:-2])
            if postal_code4 != int(origin_postcode):
                return X, Y, postal_code6
            else:
                return None
    except Exception as e:
        print(X, Y)
        return None
    
def check_same_subdistrict(X, Y, origin_postcode6):
    """Check whether the sampled house is in the same district -> object level """
    url = f"https://geodata.nationaalgeoregister.nl/locatieserver/revgeo?X={X}&Y={Y}&type=adres&rows=1&fl=*"
    response = requests.get(url)
    try:
        if response.status_code == 200:
            result = response.json()
            postal_code6 = result["response"]["docs"][0]["postcode"]
            if postal_code6 == origin_postcode6:
                return X, Y, postal_code6
            else:
                return None
    except Exception as e:
        print(X, Y)
        return None

def check_another_subdistrict(X, Y, origin_postcode6):
    """Check whether the sampled house is in another subdistrict -> subdistrict level"""
    url = f"https://geodata.nationaalgeoregister.nl/locatieserver/revgeo?X={X}&Y={Y}&type=adres&rows=1&fl=*"
    response = requests.get(url)
    try:
        if response.status_code == 200:
            result = response.json()
            postal_code6 = result["response"]["docs"][0]["postcode"]
            postal_code4 = postal_code6[:-2]
            if postal_code6 != origin_postcode6 and origin_postcode6[:-2] == postal_code4:
                return X, Y, postal_code6
            else:
                return None
    except Exception as e:
        print(X, Y)
        return None
    
def check_another_postalcode5(X, Y, origin_postcode6):
    """Check whether the sampled house is in another subdistrict -> subdistrict level"""
    url = f"https://geodata.nationaalgeoregister.nl/locatieserver/revgeo?X={X}&Y={Y}&type=adres&rows=1&fl=*"
    response = requests.get(url)
    try:
        if response.status_code == 200:
            result = response.json()
            postal_code6 = result["response"]["docs"][0]["postcode"]
            postal_code4 = postal_code6[:-2]
            postal_code5 = postal_code6[:-1]
            
            #matchh 4 digits of post
            if postal_code5 != origin_postcode6[:-1] and origin_postcode6[:-2] == postal_code4:
                return X, Y, postal_code6
            else:
                return None
    except Exception as e:
        print(X, Y)
        return None

if __name__ == "__main__":
    #district level
    # print(check_district(81837, 450207, '2286'))

    # #object level
    # ans = check_same_subdistrict(81837, 450207, '2287BD')
    # print(ans)

    #subdistrict level
    # ans = check_another_subdistrict(81793, 450159,"2287BD")
    # print(ans)

    #postal code 5
    ans = check_another_postalcode5(81615, 450127,"2287BD")
    print(ans)

    ans = get_postcode(81793, 450159)

    X = rdconverter.gps2X(52.18920997675425, 4.43839952783072)
    Y = rdconverter.gps2Y(52.18920997675425, 4.43839952783072)

    # rdx = rdconverter.gps2X(data['lat'],data['lng'])
    # rdy = rdconverter.gps2Y(data['lat'],data['lng'])
    ans = get_housenumber(X, Y)

    print(ans)

