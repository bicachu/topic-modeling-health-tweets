"""
@author: John Bica
Script to pre-process and merge csvs into one single data-frame
"""

import glob
import pandas as pd

data_dir = 'input/'           # directory to hold all target input CSV files

# Read in CSVs into merged data frame
tweets_df = pd.concat([pd.read_csv(file) for file in glob.glob(data_dir+'*.csv')], ignore_index=True)

# Drop any columns with nan values in remaining data set
tweets_df = tweets_df.dropna(axis='columns')

# Drop any un-necessary columns not needed
tweets_df = tweets_df.drop(columns=['conversation_id', 'created_at', 'cashtags', 'user_id',
                                    'user_id_str', 'link', 'search', 'reply_to'])

# Remove any duplicates based on exact tweet matches
tweets_df.drop_duplicates(keep=False, inplace=True, subset="tweet")

# Export preprocessed clean data set to csv
tweets_df.to_csv(r'input/health_tweets.csv', index=False, header=True)


