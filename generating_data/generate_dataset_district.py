#Code from Thijs Simons is used: https://github.com/SimonsThijs/wateroverlast
# import rdconverter
import sys
import os 
# setting path
sys.path.append(os.getcwd())


# import rdconverter
from neerslag import precipitation_nl
from layer import ahn_layer
from datetime import datetime
import pandas as pd
import random
import time
import numpy as np
from RD_to_postal_code_api import check_district
from BAG import home_sampler, rdconverter
from math import radians, cos, sin, asin, sqrt

# Date time variables
begin = '2016-01-02 00:00:00'
end = '2022-12-31 23:59:59'
strfformat = "%Y-%m-%d %H:%M:%S"
strfformat_ensurance = "%d/%m/%Y"

dire = os.getcwd()
# input_file = f"postcode6_number3.json"
# input_file = f"postcode6_number1.json"
# input_file = f"postcode5_number3.json"
input_file = f"parsed_w_transform_precise_coords_complete.json"

# output_file = "district_1_2022-2016_output_with_postcode_range_2k_to_4k_close_random.pkl"
output_file = "object3_district.pkl"
# output_file = "sub_district3_district.pkl"
# output_file = "postcode5_3_district.pkl"
# output_file = "district3.pkl"

print(input_file)
print(output_file)
# Time variables
total = 0
count = 0
btime = time.time()

# Rain threshold
rain_treshold = 500


def parse_datetime(data, ensurance=False):
    if ensurance:
        return datetime.strptime(str(data['date']).strip(), strfformat_ensurance)
    return datetime.strptime(str(data['date']).strip(), strfformat)


def get_precipitation_data_ensurance(row):
    date = row['date']

    global count
    count += 1
    now = time.time()
    avg_time = (now-btime)/count
    left = total-count
    if count % 10 == 0:
        print('====== rain ')
        print('time spent', now-btime)
        print('did', count, 'examples')
        print('avg', avg_time)
        print('left', left)
        print('time left', left*avg_time)
        print('======')
    lat = row['lat']
    lon = row['lng']
    rain = PNL.get_precipation_data_past_hours_list(date.year, date.month, date.day, 23, 59, lat, lon, 24)
    peak = 0
    for idx, sum in enumerate(rain):
        sum_3hours = sum + rain[idx + 1] + rain[idx + 2]
        if sum_3hours > peak:
            peak = sum_3hours
    return peak


def get_precipitation_data(row):
    global count
    count += 1
    now = time.time()
    avg_time = (now-btime)/count
    left = total-count
    if count % 10 == 0:
        print('====== rain ')
        print('time spent', now-btime)
        print('did', count, 'examples')
        print('avg', avg_time)
        print('left', left)
        print('time left', left*avg_time)
        print('======')

    date = row['date']
    date = datetime.strptime(str(row['date']), strfformat)
    lat = row['lat']
    lon = row['lng']

    return get_past3hours(date, lat, lon)


def get_past3hours(date, lat, lon):
    rain = PNL.get_precipation_data_past_hours_list(date.year, date.month, date.day, date.hour, date.minute, lat, lon, 3)
    return sum(rain)


# Step 1: Loading file and assigning target value
# df1 = pd.read_json(f"{dire}/resolution/district/{input_file}")
df1 = pd.read_json(f"{dire}/resolution/object/{input_file}")
# df1 = pd.read_json(f"{dire}/resolution/subdistrict/{input_file}")
# df1 = pd.read_json(f"{dire}/resolution/postalcode5/{input_file}")
df1 = df1.dropna()
df1['target'] = 1

# Step 2: Filter out dates which are out of the scope
df1['date'] = df1.apply(parse_datetime, axis=1)
df1 = df1[(begin < df1['date']) & (df1['date'] < end)]

# Step 3: Enrich instances with rain information
PNL = precipitation_nl.PrecipitationNL(queue_size=300)
total = len(df1)
count = 0
btime = time.time()
df1 = df1.sort_values(by=['date'])
df1['past3hours'] = df1.apply(get_precipitation_data, axis=1)

# Step 4: Filter out water damage notifications which are not caused by rain
df1 = df1[(df1.past3hours > rain_treshold)]

# Step 5: Add height layer as a feature
total = len(df1)
count = 0
btime = time.time()
ahn = ahn_layer.AHNLayer()


def add_layers(data):
    try:
        global count
        count += 1
        now = time.time()
        avg_time = (now-btime)/count
        left = total-count
        if count % 10 == 0:
            print('====== layers ')
            print('time spent', now-btime)
            print('did', count, 'examples')
            print('avg', avg_time)
            print('left', left)
            print('time left', left*avg_time)
            print('======')

        lat = data['lat']
        lng = data['lng']
        rdx = rdconverter.gps2X(lat, lng)
        rdy = rdconverter.gps2Y(lat, lng)

        x, y = round(rdx, 2), round(rdy, 2)
        d = 5
        arr = ahn.get_gdal_dataset(x-d, x+d, y-d, y+d)
        arr = arr.ReadAsArray()
        return arr
    except Exception as e:
        # print(e)
        return None


df1['layers'] = df1.apply(add_layers, axis=1)


print("adding negative samples")
# Step 6: Add negative examples
data0 = {'target': [],'lat':[], 'lng':[], 'date':[], 'zipcode':[], 'distance':[]}

HM = home_sampler.HomeSampler()
n = 5
track = []

total = len(df1)
count = 0
btime = time.time()

def distance(lat1, lon1,lat2, lon2):
     
    # radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
      
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
 
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return(c * r)

#sample houses in another district
def sample_random_houses_close(data):
    rdx = rdconverter.gps2X(data['lat'],data['lng'])
    rdy = rdconverter.gps2Y(data['lat'],data['lng'])
    origin_postcode = data['zipcode']
    
    if len(origin_postcode) == 6:
        origin_postcode = data['zipcode'][:-2]
        
    da = HM.sample_in_range(rdx, rdy, 4000, 2000, n)
    _min = 2000
    _max = 4000
    try:
        global count
        count += 1
        now = time.time()
        avg_time = (now-btime)/count
        left = total-count
        if count % 10 == 0:
            
            print('====== sample district ')
            print('time spent', now-btime)
            print('did', count, 'examples')
            print('avg', avg_time)
            print('left', left)
            print('time left', left*avg_time)
            print('======')
        
        home_lst = []
        # Try to sample 3 times
        for tries in range(3):
            if len(da) == 0:
                continue
            
            # Another try to sample if failed and increase range
            if tries > 0:
                print('another try')
                da = HM.sample_in_range(rdx, rdy, _max, _min, 5)
                # _min += 500
                _max += 500
                if len(da) == 0 and tries == 2:
                    print("No samples are being returned")
                    continue
            
            #Close sample
            min_distance = float('inf')
            for home in da:
                home = check_district(home[0], home[1], origin_postcode)
                if home is not None:
                    #another district
                    home_lst.append(home) 
            if len(home_lst) > 0:
                break
        
        da = [random.choice(home_lst)]
        lat = rdconverter.RD2lat(da[0][0], da[0][1])
        lng = rdconverter.RD2lng(da[0][0], da[0][1])
        zipcode = da[0][-1]
        min_distance = distance(lat, lng, data['lat'], data['lng'])
        
        data0['lat'].append(lat)
        data0['lng'].append(lng)
        data0['date'].append(data['date'])
        data0['zipcode'].append(zipcode)
        data0['target'].append(0)
        data0['distance'].append(min_distance)
        print("data added")
         
    except Exception as e:
        print(f"{e}")
        # print("deleted date", data["date"])
        data0['lat'].append(data['lat'])
        data0['lng'].append(data['lng'])
        data0['date'].append(data['date'])
        data0['zipcode'].append(origin_postcode)
        data0['target'].append(0)
        data0['distance'].append(0)
        track.append(data['date'])

#Adding negatives examples
df1['distance'] = 0
df1.apply(sample_random_houses_close, axis=1)
# print(f"{missing=}")
df0 = pd.DataFrame(data0)
total = len(df0)
count = 0
btime = time.time()
df0 = df0.sort_values(by=['date'])
df0['past3hours'] = df0.apply(get_precipitation_data, axis=1)

total = len(df0)
count = 0
btime = time.time()
df0['layers'] = df0.apply(add_layers, axis=1)

df = pd.concat([df0, df1], ignore_index=True)
df = df.sort_values(by=['date'])
print(f"Before applying deleted track: {len(df)}")
df = df[~df['date'].isin(track)]
print(f"After applying deleted track: {len(df)}")

#ahn = ahn_layer.AHNLayer()
#total = len(df)
#count = 0
#btime = time.time()
#df['layers'] = df.apply(add_layers, axis=1)

num_rows = len(df) // 2
group = np.array([[i] * 2 for i in range(num_rows)]).flatten()
df['group'] = group
df = df.reset_index(drop=True)

# Step 7: Output dataframe as pkl to keep the size of the file small
print(df)
df.to_pickle(f"{dire}/pkl/object/{output_file}", protocol=4)
