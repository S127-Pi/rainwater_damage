import pandas_read_xml as pdx
import os
from pandas_read_xml import flatten, fully_flatten, auto_separate_tables

dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)
file = "data/9999VBO08012023/9999VBO08012023-000001.xml"

df = pdx.read_xml(f"{dir_path}/{file}", 
	['sl-bag-extract:bagStand', 'sl:standBestand', 'sl:stand'])

key_columns = ['Objecten:naam', 'Objecten:type', 'Objecten-ref:WoonplaatsRef', 'Objecten:identificatie']
df = pdx.fully_flatten(df, key_columns)
# df = pdx.flatten(df)

# print(df)

print(df.iloc[1])