import sys
import os 
# setting path
sys.path.append(os.getcwd())

import pandas as pd 
import random
import warnings
import numpy as np 
import os.path as path
from sklearn.ensemble import RandomForestClassifier
from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import GroupKFold, RandomizedSearchCV, HalvingRandomSearchCV
from sklearn.model_selection import GroupKFold
from sklearn.metrics import confusion_matrix, precision_score, recall_score
from sklearn import metrics
from matplotlib import pyplot as plt

all_path = ["district1.pkl", "district2.pkl", "district3.pkl"]

for path in all_path:
        print(f"Current data set:{path}")
        begin_path = os.getcwd()
        resultFolder = f"{begin_path}"

        file_path = f"{begin_path}/results/texts_results/district.txt"

        if os.path.exists(file_path):
                print("The file already exists.")
                resultFile = open(f"{begin_path}/results/texts_results/district.txt", "a+")
        else:
                print("The file does not exist.")
                resultFile = open(f"{begin_path}/results/texts_results/district.txt", "w+") 
        column = 'layers'

        track = []
        def normalize(row):
                # Catch the warning
                with warnings.catch_warnings():
                        warnings.simplefilter("error", RuntimeWarning)
                        try:
                                height = row[column]
                                nans = height > 1000
                                height[nans] = np.nan
                                height = (height-np.nanmean(height))/np.nanstd(height)
                                height[np.isnan(height)] = 3
                                return height
                        except RuntimeWarning as e:
                                print(f"Caught warning: {e}")
                                print(row.date)
                                track.append(row.date)
                                height[nans] = 0
                                return height
        def reshape(arr):
                result = np.reshape(arr[column], (20,20))
                result = result.flatten()
                dfArr = pd.DataFrame(result)
                dfArr = dfArr.transpose()
                arr = arr.to_frame()
                arr = arr.drop("layers")
                arr = arr.transpose()
                arr = arr.reset_index()
                dfArr = dfArr.reset_index()
                arr = arr.join(dfArr, lsuffix="l")
                listofarr.append(arr)
                


        accuracyResult = []
        precisionResult = []
        recallResult = []
        totalConfusion = [[0,0],[0,0]]


        listofarr = []
        # path = "district_1_2022-2016_output_with_postcode_range_2k_to_4k_random_4neg.pkl"
        # path = "district_2_2022-2016_output_with_postcode_range_2k_to_4k_close_random.pkl"
        # path = "postcode4.pkl"

        print(f"file:{path}")
        df = pd.read_pickle(f"{begin_path}/pkl/district/{path}").reset_index()
        print(df.head(1))
        # df = df.sort_values(by=['date'])
        # print(df.head(2))
        if 'group' not in df.columns:
                num_rows = len(df) // 2
                group = np.array([[i] * 2 for i in range(num_rows)]).flatten()
                df['group'] = group
                df = df.reset_index(drop=True)

        df = df[["date","target", "layers", "past3hours", "group"]]
        df_original = df.copy()
        df = df.dropna()
        try:
                dropped_rows = df_original[~df_original.index.isin(df.index)]['date']
                df = df.loc[~df['date'].isin(dropped_rows)]
        except Exception as e:
                print("No data deleted")
                
        df = df[["date","target", "layers", "past3hours", "group"]]
        # df = df[["date","target", "layers", "past3hours"]]
        print(len(df))
        df[column] = df.apply(normalize, axis=1)
        print("Normalization done")
        df[column] = df.apply(reshape, axis=1)
        print("Reshaping done")
        concat_df = pd.concat(listofarr)

        #Debug empty sequence
        print(f"Before applying deleted track: {len(concat_df)}")
        concat_df = concat_df[~concat_df['date'].isin(track)]
        print(f"After applying deleted track: {len(concat_df)}")


        df = concat_df.dropna(axis="columns", how="all")
        df = df.reset_index(drop=True)

        df= df.drop(columns=['indexl','date', 'index'])
        # print(df.head(1))

        df["target"] = df["target"].astype(int)
        df["group"] = df["group"].astype(int)

        # print(df.head(2))
        
        labels = np.array(df['target'])
        groups = np.array(df['group'])

        #set features and convert to numpy array

        features= df.drop(columns=['target', 'group'])
        # features= df.drop(columns=['target'])
        print(len(features.columns))

        # Saving feature names for later use
        feature_list = list(features.columns)

        features = np.array(features)

        #group k-fold cross validation
        gkf = GroupKFold(n_splits=10)


        mape = []
        treeNumber = 0
        accuracyResult = []
        precisionResult = []
        recallResult = []
        totalConfusion = [[0,0],[0,0]]
        
        rf = RandomForestClassifier(random_state = 42, n_estimators=1000, 
                        max_depth=5, min_samples_split=2, min_samples_leaf=1)  

        for i, (train_index, test_index) in enumerate(gkf.split(features, labels, groups)):
                # print("Train: ", train_index, " Test: ", test_index)
                print(f"Fold {i}:")
                train_features, test_features = features[train_index], features[test_index]
                train_labels, test_labels = labels[train_index], labels[test_index]

                #print(test_features[0])
                #train and test the decision tree
                
                # rf = RandomForestClassifier(random_state = 42, n_estimators=1000, 
                #                         max_depth=5, min_samples_split=2, min_samples_leaf=1)        
                rf.fit(train_features, train_labels)
                label_prediction = rf.predict(test_features)
                
                confusion = confusion_matrix(test_labels,label_prediction)
                totalConfusion[0][0] += confusion[0][0]
                totalConfusion[0][1] += confusion[0][1]
                totalConfusion[1][0] += confusion[1][0]
                totalConfusion[1][1] += confusion[1][1]

                accuracyResult.append(metrics.accuracy_score(test_labels, label_prediction))
                precisionResult.append(precision_score(test_labels, label_prediction))
                recallResult.append(recall_score(test_labels, label_prediction))

                resultFile.write("Fold "+str(treeNumber)+"\n")
                resultFile.write(str(confusion)+'\n')
                resultFile.write("Accuracy: "+str(metrics.accuracy_score(test_labels, label_prediction))+"\n")
                resultFile.write("Precision: "+str(precision_score(test_labels, label_prediction))+"\n")
                resultFile.write("Recall: "+str(recall_score(test_labels, label_prediction)) + "\n\n")
                print(str(metrics.accuracy_score(test_labels, label_prediction)))
                # tree = rf.estimators_[4]# Import tools needed for visualization
                # from sklearn.tree import export_graphviz
                # import pydot# Pull out one tree from the forest
                # tree = rf.estimators_[5]# Export the image to a dot file
                # outputFile = resultFolder+"tree"+str(treeNumber)+".dot"
                # export_graphviz(tree, out_file = outputFile, feature_names = feature_list, rounded = True, precision = 1)# Use dot file to create a graph
                # #(graph, ) = pydot.graph_from_dot_file('tree.dot')# Write graph to a png file
                # #graph.write_png('tree.png')
                treeNumber+=1

                #output cross validation performance
                #all_accuracies = cross_val_score(estimator=rf, X=features, y=labels, cv=10)
        print('Analysis done!')
        # fig, ax = plt.subplots()
        # data = [accuracyResult, precisionResult, recallResult]
        # xlabels = ["Accuracy", "Precision", "Recall"]
        # ax.boxplot(data, widths= 0.50)
        # ax.set_xticklabels(xlabels)
        # ax.set_ylim(0,1)

        resultFile.write("\nAverage Accuracy: "+str(np.average(accuracyResult))+"\n")
        resultFile.write("Average Precision: "+str(np.average(precisionResult))+"\n")
        resultFile.write("Average Recall: "+ str(np.average(recallResult))+"\n")
        resultFile.write("Total Confusion matrix: \n["+str(totalConfusion[0][0])+","+ str(totalConfusion[0][1])+"] \n"+"["+str(totalConfusion[1][0])+","+ str(totalConfusion[1][1])+"] \n")
        #print(cross_val_score(estimator=rf, X=features, y=labels, cv=skf, scoring="accuracy"))
        # plt.savefig("Subdistrict_Measures_today.png")
