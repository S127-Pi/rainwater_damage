


import pandas_read_xml as pdx
import pandas as pd
import numpy as np
import os

import time

final_df = pd.DataFrame()

dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)
times = []

for i in range(1,1773):
	begint = time.time()
	file = "data/9999VBO08012023/9999VBO08012023-{:06d}.xml".format(i)
	print(f'{dir_path}/{file}')
	# df = pdx.read_xml(f"{dir_path}/{file}", 
	# 	['sl-bag-extract:bagStand', 'sl:standBestand', 'sl:stand'])
	df = pdx.read_xml(f"{dir_path}/{file}", 
		['sl-bag-extract:bagStand', 'sl:standBestand', 'sl:stand'])
	print(df)
	key_columns = ['Objecten:naam', 'Objecten:type', 'Objecten-ref:WoonplaatsRef', 'Objecten:identificatie']
	print(df)
	df = pdx.fully_flatten(df)
	# print(len(df.drop_duplicates(subset='sl-bag-extract:bagObject|Objecten:Verblijfsobject|Objecten:identificatie|#text', keep="last")))
	# df = pdx.flatten(df)
	# print("test")
	# print(df.iloc[1])
	cols = ['sl-bag-extract:bagObject|Objecten:Verblijfsobject|Objecten:voorkomen|Historie:Voorkomen|Historie:eindGeldigheid', 
				'sl-bag-extract:bagObject|Objecten:Verblijfsobject|Objecten:geometrie|Objecten:punt|gml:Point|gml:pos', 
				'sl-bag-extract:bagObject|Objecten:Verblijfsobject|Objecten:heeftAlsHoofdadres|Objecten-ref:NummeraanduidingRef|#text',
				'sl-bag-extract:bagObject|Objecten:Verblijfsobject|Objecten:identificatie|#text'
				]

	df = df[cols]
	# we dont want the duplicates
	df = df[pd.isna(df['sl-bag-extract:bagObject|Objecten:Verblijfsobject|Objecten:voorkomen|Historie:Voorkomen|Historie:eindGeldigheid'])]
	df = df.drop_duplicates(subset='sl-bag-extract:bagObject|Objecten:Verblijfsobject|Objecten:identificatie|#text', keep='last')
	final_df = pd.concat([final_df, df], ignore_index=True)
	print("ja")
	times.append(time.time()-begint)
	meantime = (np.mean(times))
	print(meantime)
	print("time left: ", meantime*(1773-i-1))
	df.to_csv('tmp/verblijfsplaatsen{}.csv'.format(i), header=False)

# final_df.columns = ['geldigheid', 'pos', 'nummer_id', 'id']
# final_df = final_df.drop_duplicates(subset='id', keep='last')

# print(final_df[pd.isna(final_df['geldigheid'])])
