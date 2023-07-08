import pandas_read_xml as pdx
import pandas as pd
import os
import time
import multiprocessing
from pandas_read_xml import flatten

def convert_xml_to_csv(file, output):
    path = os.path.dirname(os.path.realpath(__file__))
    print(f'Begin met {file}: {time.time()}')
    df = pdx.read_xml(f"{path}/data/{file}", ['sl-bag-extract:bagStand', 'sl:standBestand','sl:stand'])
    df = df.pipe(flatten)
    
    #transposing df
    df = df.transpose()
    
    #Flat df 4 times
    df = df.pipe(flatten)
    df = df.pipe(flatten)
    df = df.pipe(flatten)
    df = df.pipe(flatten)
    
    df['pos'] = df['0|Objecten:Verblijfsobject|Objecten:geometrie|Objecten:punt|gml:Point'].apply(lambda x: x['gml:pos'] if type(x)==dict and 'gml:pos' in x else None)
    df.dropna(subset=['pos'], inplace=True)
    
    #Obtain x, y coordinates
    df['x'] = df['pos'].str.split(' ').str[0]
    df['y'] = df['pos'].str.split(' ').str[1]
    
    #Desired columns
    cols = ['0|Objecten:Verblijfsobject|Objecten:identificatie','x','y', '0|Objecten:Verblijfsobject|Objecten:heeftAlsHoofdadres|Objecten-ref:NummeraanduidingRef', '0|Objecten:Verblijfsobject|Objecten:voorkomen|Historie:Voorkomen|Historie:eindGeldigheid']
    df = df[cols]
    
    #Drop duplicates
    df = df.drop_duplicates(subset='0|Objecten:Verblijfsobject|Objecten:identificatie', keep='last')
    df = df[pd.isna(df['0|Objecten:Verblijfsobject|Objecten:voorkomen|Historie:Voorkomen|Historie:eindGeldigheid'])]
    final_df = pd.DataFrame()
    final_df = pd.concat([final_df, df], ignore_index=True)
    df.to_csv(f'{path}/data/tmp/{output}')
    
    print(f'End with {file}: {time.time()}')

def convert_xml_to_csv_parallel(file, output):
    convert_xml_to_csv(file, output)


if __name__ == '__main__':
    
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        files_outputs = [(f"9999VBO08012023/9999VBO08012023-{str(i).zfill(6)}.xml", f'verblijfsplaatsen{i}.csv') for i in range(1, 2170)]
        pool.starmap(convert_xml_to_csv_parallel, files_outputs)
    