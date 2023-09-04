# Rainwater damage

This repository aims to provide tools to build datasets and machine learning models that predict rainwater damage instances at various spatial resolutions.


## Subfolders
### /Analysis
This folder contains Python files that are needed to perform analysis of predicting rainwater damage at various spatial resolutions.

### /BAG
Contains scripts that are needed to perform the proximity sampling method. <br />
Please download the following files (the files are stored in a directory e.g: 9999VBO08012023): https://www.kadaster.nl/-/kosteloze-download-bag-2-0-extract <br />
Alternatively the "verblijfplaatsen_longer.csv" can be downloaded at the following link: https://drive.google.com/file/d/16c8qa206CzjywhOs7CkjrSubp2IE8LWZ/view

### /generating_data
This folder contains scripts to generate train data at various spatial resolutions.

### /neerslag
Contains scripts that are needed to retrieve rainfall data.
The rain data is obtained from https://dataplatform.knmi.nl/catalog/datasets/index.html?x-dataset=rad_nl25_rac_mfbs_5min&x-dataset-version=2.0. <br />
Make sure the data is placed like: 'neerslag/data/{year}/{month}/RAD_NL25_RAC_MFBS_5min_XXXXXXXXXXXX_NL.h5'.

### /P2000
Contains scripts that retrieve positive rainwater damage instances from the P2000 network.

### /pkl
Contains pkl files for the purpose of training and testing. 
Notice that the amount of positive rainwater damage instances is equal to the number of negative rainwater damage instances. 
This results in balanced training and testing data.

### /sampler
Contains scripts that sample negative rainwater damage instances at various spatial resolutions.

### /stats_tests
Contains scripts to perform statistical tests.

## Acknowledgements

 - [regenwateroverlast](https://github.com/SimonsThijs/wateroverlast)
 - [predicting_raindamage](https://github.com/teundemast/regenwater_overlast)


## Contact
For questions related to this repository can be send to: S_molling@hotmail.com
