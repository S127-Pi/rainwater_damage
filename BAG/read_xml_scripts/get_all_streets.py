import pandas_read_xml as pdx
import pandas as pd
import os

final_df = pd.DataFrame()
dir_path = os.path.dirname(os.path.realpath(__file__))

for i in range(1,35):
    file = "data/9999OPR08012023/9999OPR08012023-{:06d}.xml".format(i)
    df = pdx.read_xml(f"{dir_path}/{file}", 
		['sl-bag-extract:bagStand', 'sl:standBestand', 'sl:stand'])
    key_columns = ['Objecten:naam', 'Objecten:type', 'Objecten-ref:WoonplaatsRef', 'Objecten:identificatie']
    df = pdx.fully_flatten(df, key_columns)
    
    cols = ['sl-bag-extract:bagObject|Objecten:OpenbareRuimte|Objecten:identificatie|#text', 
				'sl-bag-extract:bagObject|Objecten:OpenbareRuimte|Objecten:naam', 
				'sl-bag-extract:bagObject|Objecten:OpenbareRuimte|Objecten:ligtIn|Objecten-ref:WoonplaatsRef|#text'
				]
    df = df[cols]
    final_df = pd.concat([final_df, df], ignore_index=True)
    
final_df.columns = ['id', 'naam', 'woonplaatsid']
final_df.drop_duplicates()
final_df.to_csv('straatnamen.csv')