#Python script for pulling data from the Twitter API and analyzing it into a pandas dataframe

#Resources used:
#https://www.youtube.com/watch?v=ujId4ipkBio&ab_channel=ComputerScience
#https://www.youtube.com/watch?v=bNDRiaFyLrs&ab_channel=Algovibes

import tweepy
import pandas as pd
import numpy as np
import json
from datetime import datetime
from textblob import TextBlob

import util
import public_keys


api_key = public_keys.twitter_api_key
api_secret = public_keys.twitter_api_secret
access_token = public_keys.twitter_access_token
access_token_secret = public_keys.twitter_access_token_secret
bearer_token = public_keys.twitter_bearer_token

auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit = True)
start_date = datetime(2020, 11, 7, 0, 0, 0)
end_date = datetime(2021, 1, 7, 0, 0, 0)

df = pd.read_csv('../static_data/updated_legislators.csv')
curr_reps = df[(df['title'] == 'Rep')]
curr_reps_twit = curr_reps.dropna(subset = ['twitter_id'])

districts = curr_reps_twit['district'].tolist()
states = curr_reps_twit['state'].tolist()
statexdistrict = [tup for tup in tuple(zip(states, districts))]
twitters = curr_reps_twit['twitter_id'].tolist()


def map_district_twitter():
    '''
    Returns a dictionary with congressional district to the appropriate representative's twitter
    '''
    dist_twit = {}
    for i, v in enumerate(statexdistrict):
        if v not in dist_twit:
            dist_twit[v] = [twitters[i]]
        else:
            dist_twit[v].append(twitters[i])
    return dist_twit


st_dist_twit = map_district_twitter() #gets a dictionary with district key and representative's twitter value


def pull_tweets(handle, maxid, num):
    '''
    Inputs:
        handle (str): A twitter handle, for a US Representative
        maxid (str): An ID for the last tweet pulled, all subsequent tweets will be before this one
        num (int): number of tweets we want to pull

    Returns the tweepy objects corresponding to each tweet
    '''
    return api.user_timeline(screen_name = handle, max_id = maxid, count = num, lang='en', tweet_mode='extended')
    # max tweets you can pull from a user is 200


def get_df(state, district):
    '''
    Inputs:
        state (str): state of the congressional district
        district (str): value of the congressional district

    Returns a dataframe containing tweets from the dictrict's representative and a sentiment analysis
    '''
    twitters = st_dist_twit[(state, district)]
    tweets = []

    posts = []
    for handle in twitters:
        for i in range(0, 5): #do this to bypass the 200 tweet limit on a user, pulls 1000 most recent tweets
            if len(posts) > 0:
                post = posts[-1]
                maxid = None
                for tweet in post:
                    maxid = tweet.id #ensure that same tweets are not pulled by setting all following tweets before max_id
                posts.append(pull_tweets(handle, maxid, 200)) 
            else:
                posts.append(pull_tweets(handle, None, 200))
    posts = [tweet for post in posts for tweet in post]
    for tweet in posts:
        if tweet.created_at < end_date and tweet.created_at > start_date: #filters tweets by desired dates
            tweets.append(tweet)
    df = pd.DataFrame([tweet.full_text for tweet in tweets], columns=['Tweets'])

    df['Tweets'] = df['Tweets'].apply(util.cleantwt)
    df['Subjectivity'] = df['Tweets'].apply(util.subjectivity)
    df['Polarity'] = df['Tweets'].apply(util.polarity)
    df['Analysis'] = df['Polarity'].apply(util.analysis)

    return df


def aggregate(df):
    '''
    Inputs:
        df (dataframe)

    Returns a tuple consisting of aggregate sentiment analysis scores
    '''
    if len(df) != 0:
        pos = len(df[(df['Analysis'] == 'Positive')])/len(df)
        neut = len(df[(df['Analysis'] == 'Neutral')])/len(df)
        neg = len(df[(df['Analysis'] == 'Negative')])/len(df)
    else:
        pos, neut, neg = 0, 0, 0

    mean_polarity = df['Polarity'].mean()
    mean_subjectivity = df['Subjectivity'].mean()

    return (pos, neut, neg, mean_polarity, mean_subjectivity)


def create_csv():
    '''
    Creates a csv file that presents aggregated twitter data for all districts'
    representatives in the United States. Raw data is saved to a separate csv.
    '''
    print('Starting process for aggregating all representative twitter data over the timeframe.')
    print('Buckle up! This will take about 40 minutes, the process analyzes hundreds of thousands of tweets.')
    print('Last generated csv is in the generated_data folder, titled Aggregated_Twitter_Rep_Data.csv')

    data = {'State': [], 'District': [], 'Rep': [], 'Number_of_Tweets': [], 'Common_Words': [], 'Mean_Subjectivity': [], 
    'Mean_Polarity': [], 'Percent_Positive': [], 'Percent_Negative': [], 'Percent_Neutral': []}

    raw_tweet_data = {'Account': [], 'Tweet': []}

    for key, val in st_dist_twit.items():
        state, district = key
        try:
            single_df = get_df(state, district)
            raw_tweet_data['Account'].append(val)
            raw_tweet_data['Tweet'].append(single_df['Tweets'].tolist())
        except tweepy.TweepError:
            print("Failed to pull data on this account, skipping ", key, val)

        pos, neut, neg, mean_polarity, mean_subjectivity = aggregate(single_df)
        keywords = util.get_keywords(single_df["Tweets"])

        data['State'].append(state)
        data['District'].append(district)
        data['Rep'].append(val)
        data['Number_of_Tweets'].append(len(single_df))
        data['Common_Words'].append(keywords)
        data['Mean_Subjectivity'].append(mean_subjectivity)
        data['Mean_Polarity'].append(mean_polarity)
        data['Percent_Positive'].append(pos)
        data['Percent_Negative'].append(neg)
        data['Percent_Neutral'].append(neut)

    raw_data_df = pd.DataFrame(data = raw_tweet_data)

    raw_data_df.to_csv('../generated_data/Raw_Data_Rep_Tweets.csv')

    df = pd.DataFrame(data = data)

    df.to_csv('../generated_data/Aggregated_Twitter_Rep_Data.csv')
