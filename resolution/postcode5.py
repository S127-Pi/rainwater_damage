import pandas as pd
import os
import json

dire = os.getcwd()
df = pd.read_csv(f"{dire}/resolution/pc6hnr20210801_gwb.csv", delimiter=";")

result = {}

for postcode in df['PC6']:
    key = postcode[:5]
    if key in result:
        result[key].append(postcode)
        result[key] = list(set(result[key]))
    else:
        result[key] = [postcode]

with open(f"{dire}/resolution/postcode5.txt", "w+") as f:
    f.write(json.dumps(result, indent=4))
print("Done!")
