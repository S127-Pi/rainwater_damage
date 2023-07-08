#Code from Thijs Simons is used: https://github.com/SimonsThijs/wateroverlast

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
import numpy as np
import time
from BAG import rdconverter
from sampler import negsampler
from RD_to_postal_code_api import check_another_subdistrict


# Date time variables
begin = '2016-01-02 00:00:00'
end = '2022-12-31 23:59:59'
strfformat = "%Y-%m-%d %H:%M:%S"
strfformat_ensurance = "%d/%m/%Y"

dire = os.getcwd()
input_file = "postcode6_number3.json"
output_file = "sub_district3_normal.pkl"
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
df1 = pd.read_json(f"{dire}/resolution/subdistrict/{input_file}")
df1 = df1.dropna()
df1['target'] = 1
# df1 = df1.drop("zipcode", axis=1)

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

# #Step 5: Add height layer as a feature
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
        print(e)
        return None


df1['layers'] = df1.apply(add_layers, axis=1)
# df1 = df1.drop(columns=['lat', 'lng'])

# Step 6: Add negative examples
# data0 = {'target': [], 'past3hours': [], 'layers': [], "date": [], 'bouwjaar':[]}
data0 = {'target': [],'lat':[], 'lng':[], 'date':[], 'past3hours':[], 'zipcode':[]}

# HM = home_sampler.HomeSampler()
HM = negsampler.Sampler()
n = 5
track = []

total = len(df1)
count = 0
btime = time.time()

#sample random house in another subdistrict
def sample_random_houses_close(data):
    # rdx = rdconverter.gps2X(data['lat'],data['lng'])
    # rdy = rdconverter.gps2Y(data['lat'],data['lng'])
    origin_postcode = data['zipcode']
    da = HM.add_negative_subdistrict(origin_postcode, n)
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
        
        #try to sample 3 times
        for tries in range(3):
            if len(da) == 0:
                continue
            #Another try to sample
            if tries > 0:
                print("another try")
                da = HM.add_negative_subdistrict(origin_postcode, n)
            if len(da) == 0 and tries == 2:
                print("No samples are being returned")
            
            for home in da:
                rdx = rdconverter.gps2X(home[0], home[1])
                rdy = rdconverter.gps2Y(home[0], home[1])
                home = check_another_subdistrict(rdx, rdy, origin_postcode)
                if home is not None:
                    home_lst.append(home)
            #houses found
            if len(home_lst) > 0:
                break
        #Choose one random house in another subdistrict
        da = [random.choice(home_lst)]
        lat = rdconverter.RD2lat(da[0][0], da[0][1])
        lng = rdconverter.RD2lng(da[0][0], da[0][1])
        zipcode = da[0][-1]
        data0['lat'].append(lat)
        data0['lng'].append(lng)
        data0['date'].append(data['date'])
        data0['zipcode'].append(zipcode)
        data0['past3hours'].append(data['past3hours'])
        data0['target'].append(0)
        print("data added")
        
                       
    except Exception as e:
        print("empty sequence")
        print("deleted date", data["date"])
        data0['lat'].append(0)
        data0['lng'].append(0)
        data0['zipcode'].append(origin_postcode)
        data0['date'].append(data['date'])
        data0['past3hours'].append(data['past3hours'])
        data0['target'].append(0)
        track.append(data['date'])

#Adding negatives examples
df1.apply(sample_random_houses_close, axis=1)
df0 = pd.DataFrame(data0)

total = len(df0)
count = 0
btime = time.time()
df0 = df0.sort_values(by=['date'])
# df0['past3hours'] = df0.apply(get_precipitation_data, axis=1)

total = len(df0)
count = 0
btime = time.time()
df0['layers'] = df0.apply(add_layers, axis=1)

df = pd.concat([df0, df1], ignore_index=True)
df = df.sort_values(by=['date'])
print(f"Before applying deleted track: {len(df)}")
df = df[~df['date'].isin(track)]
print(f"After applying deleted track: {len(df)}")


num_rows = len(df) // 2
group = np.array([[i] * 2 for i in range(num_rows)]).flatten()
df['group'] = group
df = df.reset_index(drop=True)

# Step 7: Output dataframe as pkl to keep the size of the file small
print(df)
df.to_pickle(f"{dire}/pkl/sub_district/{output_file}", protocol=4)
