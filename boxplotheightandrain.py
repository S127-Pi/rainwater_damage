#Code from Teun de Mast is used: hhttps://github.com/teundemast/regenwater_overlast
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
# from collections import Counter
sns.set_style("darkgrid")

dict_height_and_rain  ={
    "Performance":[],
    "Values": [],
    "Resolution": [],
}
current_path = os.getcwd()
# files = ["object_normal.txt", "subdistrict_normal.txt", "postcode5_normal.txt","district.txt"]
# files = ["object_district.txt", "subdistrict_district.txt","postcode5_district.txt", "district.txt"]

files = ["object_normal.txt", "subdistrict_normal.txt","district.txt"]
# files = ["object_district.txt", "subdistrict_district.txt", "district.txt"]

# files = ["object_gf_normal.txt", "subdistrict_1_normal.txt", "postcode5_normal.txt", "district_2_random_gf.txt"]
for file in files:
    with open(current_path + "/results/texts_results/"+ file, "r") as f:
        all_lines = f.read().splitlines()
        for line in all_lines:
            if "Accuracy" in line and "Average" not in line:
                value = float(line.split(" ")[1])
                dict_height_and_rain["Performance"].append("Accuracy")
                dict_height_and_rain["Values"].append(value)
                if file == "object_normal.txt":
                    dict_height_and_rain["Resolution"].append("Object level")
                elif file == "subdistrict_normal.txt":
                    dict_height_and_rain["Resolution"].append("Subdistrict level")
                # elif file == "postcode5_normal.txt":
                #     dict_height_and_rain["Resolution"].append("Postal code 5")
                elif file == "district.txt":
                    dict_height_and_rain["Resolution"].append("District level")
                    
            elif "Precision" in line and "Average" not in line:
                value = float(line.split(" ")[1])
                dict_height_and_rain["Performance"].append("Precision")
                dict_height_and_rain["Values"].append(value)
                if file == "object_normal.txt":
                    dict_height_and_rain["Resolution"].append("Object level")
                elif file == "subdistrict_normal.txt":
                    dict_height_and_rain["Resolution"].append("Subdistrict level")
                # elif file == "postcode5_normal.txt":
                #     dict_height_and_rain["Resolution"].append("Postal code 5")
                elif file == "district.txt":
                    dict_height_and_rain["Resolution"].append("District level")
                    
            elif "Recall" in line and "Average" not in line:
                value = float(line.split(" ")[1])
                dict_height_and_rain["Performance"].append("Recall")
                dict_height_and_rain["Values"].append(value)
                if file == "object_normal.txt":
                    dict_height_and_rain["Resolution"].append("Object level")
                elif file == "subdistrict_normal.txt":
                    dict_height_and_rain["Resolution"].append("Subdistrict level")
                # elif file == "postcode5_normal.txt":
                #     dict_height_and_rain["Resolution"].append("Postal code 5")
                elif file == "district.txt":
                    dict_height_and_rain["Resolution"].append("District level")

df_rain = pd.DataFrame(data=dict_height_and_rain)
plt.rcParams['figure.figsize'] = (12,8)

ax = sns.boxplot(x='Performance', y='Values', hue='Resolution', data=dict_height_and_rain, width=0.5,
                  meanprops={"marker":"o",
                       "markerfacecolor":"white", 
                       "markeredgecolor":"black",
                      "markersize":"7"},
                    showmeans=True,
                    showfliers=False)
plt.ylabel("Performance", fontsize= 12)
plt.savefig("hoogtenneerslag_normal_setting.png")