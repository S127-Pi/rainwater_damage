import sys
import os 
# setting path
sys.path.append(os.getcwd())

import scipy.stats as stats
import pandas as pd
import numpy as np
import scikit_posthocs as sp

current_path = os.getcwd()
files = ["object_district.txt", 
         "subdistrict_district.txt", 
         "district.txt"]

# files = ["object_normal.txt", 
#          "subdistrict_normal.txt", 
#          "district.txt"]

model1_scores = []
model2_scores = []
model3_scores = []

for file in files:
    with open(current_path + "/results/texts_results/"+ file, "r") as f:
        all_lines = f.read().splitlines()
        for line in all_lines:
            if "Accuracy" in line and "Average" not in line:
                value = float(line.split(" ")[1])
                if file == "object_district.txt":
                    model1_scores.append(value)
                elif file == "subdistrict_district.txt":
                    model2_scores.append(value)
                elif file == "district.txt":
                    model3_scores.append(value)
                    

average_acc_model1 = np.average(model1_scores)
average_acc_model2 = np.average(model2_scores)
average_acc_model3 = np.average(model3_scores)

print(f"""
        Average accuracy model1: {average_acc_model1}
        Average accuracy model2: {average_acc_model2}
        Average accuracy model3: {average_acc_model3}
        
      """)
# Perform ANOVA test
fvalue, pvalue = stats.f_oneway(model1_scores, model2_scores, model3_scores)

# Print the results
print("F-value:", fvalue)
print("p-value:", pvalue)

# Check for statistical significance
alpha = 0.05  # Set your desired significance level

if pvalue < alpha:
    print("There are statistically significant differences between the models.")
else:
    print("There are no statistically significant differences between the models.")



# Perform the Nemenyi post-hoc test
nemenyi_results = sp.posthoc_nemenyi([model1_scores, model2_scores, model3_scores])

print(nemenyi_results)

