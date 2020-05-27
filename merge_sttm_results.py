"""
@author: John Bica
Script to pre-process and merge csvs into one single data-frame
"""

import glob
import pandas as pd

data_dir = 'data/'  # directory to hold all target input CSV files

# Read in CSVs into merged data frame
tweets_df = pd.concat([pd.read_csv(file) for file in glob.glob(data_dir+'*topics.csv')], ignore_index=True)

# Export merged data set to csv and pickle files
tweets_df.to_csv(r'data/sttm_all_topics.csv', index=False, header=True)
tweets_df.to_pkl(r'data/sttm_all_topics.pkl')


