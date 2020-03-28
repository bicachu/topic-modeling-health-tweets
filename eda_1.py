# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 20:02:00 2020

@author: Insti
"""

import os
import csv
import pandas as pd
from datetime import date
import datetime 
import twint

#update directories
directory = 'C:\\Google NEU\DS5230 Unsupervised Machine Learning & Data Mining\\Project\\data\\Health_Tweets\\'
data_sample = pd.read_csv('C:\\Users\\Insti\\Downloads\\tweets_df_sample.csv')

# Create labels for news sources
user_handle_list=['bbchealth', 'cnnhealth', 'everydayHealth', 'foxnewshealth',
                   'gdnhealth', 'goodhealth', 'khnews', 'latimeshealth',
                   'nbcnewshealth', 'nprhealth', 'nythealth', 'reuters_health',
                   'usnewshealth', 'wsjhealth', 'timehealth', 'harvardhealth']

#scrape:

#user_handle_list=['latimeshealth']
#for username in user_handle_list:
#    # filename = username+"_df"
#    c = twint.Config()
#    c.Limit = 10
#    c.Debug = False
#    c.Username = username
#    c.Pandas = True
#    c.Pandas_clean  = True
#    # c.Output = filename
#    # c.Store_pandas = True
#    twint.run.Search(c)
#Tweets_df = twint.storage.panda.Tweets_df

#old#
#idx = 0
#datasourcelist = []
#for file in os.listdir(directory):
#    df = pd.read_csv(directory+file, sep='|', header=None, error_bad_lines=False, engine='python')
#    df['label'] = sources[idx]
#    idx += 1
#    datasourcelist.append(df)
#    df.to_csv(file, header=None, sep='|', index=None)   # write out each file with labels to new txt file
#    


data_time_obj = '2020-03-28 15:47:32'
data_time_obj = datetime.datetime.strptime(data_time_obj, '%Y-%m-%d %H:%M:%S')
print(data_time_obj.weekday())

#.weekday()
#.day

#get number of tweets by year and by source
def tweetsby(data):
    #add year column
    data['Year'] = 0
#    data['2014']=0
#    data['2015']=0
#    data['2016']=0
#    data['2017']=0
#    data['2018']=0
#    data['2019']=0
#    data['2020']=0
    for i in range(len(data)):
        date_tmp = datetime.datetime.strptime(data.iloc[i][3], '%Y-%m-%d %H:%M:%S')
        if date_tmp.year == 2014:
            data.loc[i,'Year'] = 2014
        elif date_tmp.year == 2015:
            data.loc[i,'Year'] = 2015
        elif date_tmp.year == 2016:
            data.loc[i,'Year'] = 2016
        elif date_tmp.year == 2017:
            data.loc[i,'Year'] = 2017
        elif date_tmp.year == 2018:
            data.loc[i,'Year'] = 2018
        elif date_tmp.year == 2019:
            data.loc[i,'Year'] = 2019
        else:
            data.loc[i,'Year'] = 2020
    #tweets by year
    tweetbyyear_df = data.groupby(['Year']).size().reset_index(name='counts')
    #tweets by source
    tweetbysource_df = data.groupby(['username']).size().reset_index(name='counts')
    return tweetbyyear_df, tweetbysource_df

test_df1, test_df2 = tweetsby(data_sample)

#most liked tweet and most retweeted

def most_liked_rt(data):
    #most liked
    ml_tmp_df = data.groupby(['username'])['nlikes'].transform(max) == data['nlikes']
    ml_df = data[ml_tmp_df]
    #most retweeted
    mr_tmp_df = data.groupby(['username'])['nretweets'].transform(max) == data['nretweets']
    mr_df = data[mr_tmp_df]
    return ml_df, mr_df

mostliked_test, mostrt_test = most_liked_rt(data_sample)


######################old code -- save for now  ###############
#    for source in sourcelist:
#        filter_source = df['username'] == source #filter for a specific source
#        tmp_df = data[filter_source]
        
        
#is_la = data_sample['username'] == 'latimeshealth'
#data_sample_la = data_sample[is_la]
#data_sample_la.max(level = 'nlikes')

#num tweets by year
#def numtweets_year(data):
##    yr_dict = {
##            '2014': data['2014'].sum(),
##            '2015': data['2015'].sum(),
##            '2016': data['2016'].sum(),
##            '2017': data['2017'].sum(),
##            '2018': data['2018'].sum(),
##            '2019': data['2019'].sum(),
##            '2020': data['2020'].sum()}  
#    yr_list = []
#    yr_list.append(data['2014'].sum())      
#    yr_list.append(data['2015'].sum())    
#    yr_list.append(data['2016'].sum())    
#    yr_list.append(data['2017'].sum())    
#    yr_list.append(data['2018'].sum())    
#    yr_list.append(data['2019'].sum())    
#    yr_list.append(data['2020'].sum())  
#    return yr_list
#
#sum_yrs = numtweets_year(test_df)

#num tweets by source
    
#def tweetsbysource(data):
#    tweetbysource_df = data_sample.groupby(['username']).size().reset_index(name='counts')
#    return tweetbysource_df

#numtweetbysource = tweetsbysource(test_df)

#
#range(len(data_sample))
#data_sample.iloc[0][3]
#
#testdate = datetime.datetime.strptime(data_sample.iloc[0][3], '%Y-%m-%d %H:%M:%S')
#type(testdate.year)
#
#data_sample.loc[19,'nlikes'] =2
#data_sample.loc[19,'nlikes']
#        

#get the tweets per year by account
    