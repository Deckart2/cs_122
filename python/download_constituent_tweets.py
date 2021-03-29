import searchtweets as st
import pandas as pd
import json

# Set filepaths
TWEET_USER_DATA_RAW = '../generated_data/tweets/tweet_and_user_data_raw.json'
PLACE_DATA_RAW= '../generated_data/tweets/place_data_raw.json'

# Set search arguments common for each query of API
# Note: this requires credentials to be saved in ".twitter_keys.yaml".  If you
# do not have this file, the API will not run.  Requires academic license.
search_args = st.load_credentials(".twitter_keys.yaml",
                                       yaml_key="search_tweets_v2",
                                       env_overwrite=False)


def gen_query(search_string):
    '''
    Generates query object for use in the Twitter API v2 according to specific
    criteria.

    Inputs:
      - search_string (str): specific string to search for in api.

    Returns:
      - query (query object): contains all required parameters to run api.  
    '''
    query = st.gen_request_parameters(search_string, 
                                  results_per_call=500,
                                  expansions='geo.place_id,author_id',
                                  tweet_fields='id,text,author_id,created_at',
                                  user_fields='location',
                                  place_fields='full_name,place_type,geo',
                                  start_time='2020-11-03',
                                  end_time = '2021-01-08')
    return query


def get_tweets(max_calls, query, output_filename):
    '''
    Queries Twitter API using a defined query and saves results into a json file.

    Inputs:
      - max_calls: (int) maximum number of tweets (and requests) to query from API
      - query (query obj): contains all required parameters to run api. 
      - output_filename (str): filename of final json to save.

    Returns:
      - Exports json file with tweets as a list of dicts.
    '''
    rs = st.ResultStream(request_parameters=query,
                         max_requests=max_calls,
                         max_tweets=max_calls,
                         **search_args)
    tweets = list(rs.stream())
    with open(output_filename, 'w') as f:
        json.dump(tweets, f)


def get_and_save_tweets(query_api=False, 
                        searches=['''has:geo place_country:US''', 
                                  '''#stopthesteal -is:retweet'''], 
                        calls=[700000, 525000],  #700k places, 525k tweets
                        filepaths=[PLACE_DATA_RAW, TWEET_USER_DATA_RAW]):
    '''
    Queries twitter API twice according to two different queries:
      1. Get all geo-tagged tweets in the US in the timeframe
      2. Get all tweets that used #StopTheSteal in the timeframe
    
    Inputs:
      - query_api (bool): if true query api, if false, use downloaded data
      - searches: list of search strings
      - calls: list of max_calls to make to the api
      - filepaths: list of filepaths to save raw json data
    '''
    if not query_api:
        print('Using saved tweets. Did not query API. Set "query_api=True" to run.')
    else:
        print('Querying API.  This may take a few minutes.')
        for i, search in enumerate(searches):
            query = gen_query(search)
            get_tweets(max_calls=calls[i], query=query, output_filename=filepaths[i])


if __name__ == "__main__":
    get_and_save_tweets()
