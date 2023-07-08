import os
import pandas as pd



import pandas as pd
import os
import warnings

warnings.filterwarnings("ignore")


cols = ['0|Objecten:Verblijfsobject|Objecten:identificatie','x','y']
df_list = []
final_df = pd.DataFrame()
df_append = pd.DataFrame()
# for filename in os.listdir():
#     if filename.endswith(".csv"):
#         df = pd.read_csv(filename)
#         df = df.drop_duplicates(subset='0|Objecten:Verblijfsobject|Objecten:identificatie', keep='last')
#         df = df[cols]
#         df_list.append(df)
path = os.path.dirname(os.path.realpath(__file__))
for i in range(1,2170):
    file = "verblijfsplaatsen{:01d}.csv".format(i)
    print(f'Bezig met {file}')
    df_temp = pd.read_csv(f'{path}/{file}')
    df_temp = df_temp[cols]
    df_append = df_append.append(df_temp, ignore_index = True)
    print('Row count is:', len(df_append.axes[0]))

df_append = df_append.drop_duplicates(subset='0|Objecten:Verblijfsobject|Objecten:identificatie', keep='last')
file = "verblijfplaatsen_longer.csv"
df_append.to_csv(f"{path}/{file}")
print('Row count is:', len(df_append.axes[0]))
print("concatenating done!")