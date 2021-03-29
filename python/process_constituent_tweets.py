import pandas as pd
import json
import geopandas as gp
from shapely.geometry import Point, Polygon
import numpy as np
import util

# Load locations of files
CD_SHP_PATH = '../static_data/congressional_districts/cb_2019_us_cd116_500k.shp'
CSV_PATH = '../generated_data/twitter_constituent_data.csv'
TWEET_USER_DATA_RAW = '../generated_data/tweets/tweet_and_user_data_raw.json'
PLACE_DATA_RAW= '../generated_data/tweets/place_data_raw.json'
WGS84 = 4326


def load_dfs(sts_json=TWEET_USER_DATA_RAW, all_json=PLACE_DATA_RAW):
    '''
    Takes raw twitter output (in json files) and converts to workable dataframes.

    Inputs:
      - sts_json (str): json filepath of all tweets that included
        #StopTheSteal during the timeframe Nov 3, 2020 -Jan 7, 2021
      - all_json (str): json filepath of all geo-tagged tweets during same
        timeframe.

    Returns:
      - tuple of the following dataframes (in order):
        - sts_tweet_df: all tweets with #StopTheSteal, identified by tweet_id
        - sts_user_df: all users that tweeted #StopTheSteal, identified by
          author_id
        - all_tweet_df: all tweets with geo-tagged location, identified by
          tweet_id and geo.place_id
        - all_place_df: all twitter geo-tagged locations, identified by
          geo.place_id
    '''
    sts_all, geo_all = json.load(open(sts_json)), json.load(open(all_json))

    id_list = ['author_id', 'geo.place_id']
    search_list = ['users', 'places']
    df_list = []

    for i, tweets in enumerate([sts_all, geo_all]):
        tweet_list, info_list = [], []
        for tweet in tweets:
            if search_list[i] in tweet:
                info_list.extend([item for item in tweet[search_list[i]]])
            elif 'id' in tweet:
                tweet_list.append(tweet)
        info_df = pd.json_normalize(info_list).drop_duplicates(subset=['id']
                   ).rename(columns={'id': id_list[i]})
        tweet_df = pd.json_normalize(tweet_list).drop_duplicates(subset=['id']
                    ).rename(columns={'id': 'tweet_id'})
        df_list.extend([tweet_df, info_df])
    return tuple(df_list)


def match_user_locations(sts_user_df, all_place_df):
    '''
    Creates a crosswalk of twitter users to twitter locations using the twitter
    user location attached to the twitter account.

    Inputs:
      - sts_user_df: all users that tweeted #StopTheSteal, identified by
        author_id
      - all_place_df: all twitter geo-tagged locations, identified by
        geo.place_id

    Returns:
      - match_df: crosswalk between user (author_id) and location (geo.place_id)
    '''
    # Drop US location
    sts_user_df.drop(sts_user_df.loc[sts_user_df['location']=='United States'].index,
                 inplace=True)
    # Split place_df into city and state for matching
    sts_user_df[['user_city','user_state'
           ]] = sts_user_df['location'].str.split(', ', n=1, expand=True)
    all_place_df[['city','state'
            ]] = all_place_df['full_name'].str.split(', ', n=1, expand=True)

    left_cols = ['location', 'user_city', 'location', 'user_city']
    right_cols = ['full_name', 'full_name', 'city', 'city']
    match_dfs = []
    cols = ['location', 'user_city', 'author_id']

    for i, left_field in enumerate(left_cols):
        # drop duplicate fields (cities) before matching
        all_place_df = all_place_df.drop_duplicates(subset=[right_cols[i]],
                                                    keep=False)
        sts_user_df = sts_user_df.merge(all_place_df, left_on=left_field,
                              right_on=right_cols[i],how='left', indicator=True)
        match_dfs.append(sts_user_df.loc[(sts_user_df['_merge']=='both')].copy())
        sts_user_df = sts_user_df.loc[(sts_user_df['_merge']=='left_only')][cols]
    return pd.concat(match_dfs, ignore_index=True)[['author_id', 'geo.place_id']]


def bbox_to_polygon(bbox):
    '''
    Converts bbox field from twitter API into Polygon object

    Inputs:
      - bbox (list of strings): corrsponding to the lat/long coordinates of the
          two outermost corners of a bounding box of the location.

    Returns:
      - Polygon object of the bounding box.
    '''
    lon1, lat1, lon2, lat2 = bbox
    return Polygon([(lon1, lat1),(lon2, lat1),(lon1,lat2),(lon2, lat2)])


def spatial_join(all_place_df):
    '''
    Creates crosswalk of twitter places to congressional districts by spatially
    intersecting.

    Inputs:
      - all_place_df: all twitter geo-tagged locations, identified by
        geo.place_id

    Returns
      - cd_places_df: dataframe with list of all congressional districts (GEOID)
        and all corresponding twitter places (geo.place_id) that intersect the
        congressional district.
    '''
    all_place_df['geom'] = all_place_df['geo.bbox'].apply(bbox_to_polygon)
    # do not include larger than state geographies
    all_place_df = all_place_df[all_place_df['place_type'
                      ].isin(['city','poi','neighborhood']
                      )][['geo.place_id', 'geom']]
    places_gdf = gp.GeoDataFrame(all_place_df, geometry='geom'
                                ).set_crs(epsg=WGS84)
    cd_gdf = gp.read_file(CD_SHP_PATH).to_crs(epsg=WGS84)[['GEOID','geometry']]
    cd_place_gdf = gp.sjoin(cd_gdf, places_gdf, how='inner', op='intersects'
                    ).drop_duplicates()
    return cd_place_gdf[['GEOID', 'geo.place_id']]


def process_geo_all(all_tweet_df, cd_places_df):
    '''
    Analyze dataframe of all geo-tagged tweets to get the average subjectivity
    per congressional district.

    Inputs:
      - all_tweet_df: all tweets with geo-tagged location, identified by
        tweet_id and geo.place_id
      - cd_places_df: dataframe with list of all congressional districts (GEOID)
        and all corresponding twitter places (geo.place_id) that intersect the
        congressional district.

    Returns:
      - dataframe with one row per district (GEOID) and the metric listed above.
    '''
    # Perform sentiment analysis
    all_tweet_df['subjectivity'] = all_tweet_df['text'
                          ].apply(lambda x: util.subjectivity(util.cleantwt(x)))
    # Merge spatial info, and aggregate by GEOID
    all_tweet_df = all_tweet_df.merge(cd_places_df, on='geo.place_id')
    all_tweet_df = all_tweet_df.groupby(['GEOID']
                              ).agg({'subjectivity': ['mean']})
    all_tweet_df.columns = ['avg_subjectivity_geo_all']
    return all_tweet_df.reset_index()


def process_loc_sts(sts_tweet_df, match_df, cd_places_df):
    '''
    Analyze dataframe of all #StopTheSteal tweets to get several metrics:
      - common keywords per district
      - count of tweets using #StopTheSteal
      - count of unique users

    Inputs:
      - sts_tweet_df: all tweets with #StopTheSteal, identified by tweet_id
      - match_df: crosswalk between user (author_id) and location (geo.place_id)
      - cd_places_df: dataframe with list of all congressional districts (GEOID)
        and all corresponding twitter places (geo.place_id) that intersect the
        congressional district.

    Returns:
      - dataframe with one row per district (GEOID) and the above metric.
    '''
    # Perform sentiment analysis
    sts_tweet_df['clean_text'] = sts_tweet_df['text'].apply(util.cleantwt)
    # Drop old geo.place_id if it exists
    sts_tweet_df = sts_tweet_df[['tweet_id','clean_text','author_id']]

    # Merge spatial data, and aggregate by GEOID

    sts_tweet_df = sts_tweet_df.merge(match_df, on='author_id'
                              ).merge(cd_places_df, on='geo.place_id')
    sts_tweet_df = sts_tweet_df.groupby(['GEOID']).agg(
                                {'clean_text': util.get_keywords,
                                'tweet_id': 'nunique', 'author_id': 'nunique'})
    sts_tweet_df.columns = ['keywords_loc_sts', 'tweet_cnt_loc_sts',
                            'users_cnt_loc_sts']
    return sts_tweet_df.reset_index()


def go():
    '''
    Main function to execute all steps in processing const. tweets.
    '''
    # 1. Load all data
    print('Loading constituent tweets...')
    sts_tweet_df, sts_user_df, all_tweet_df, all_place_df = load_dfs()

    # 2. Match user locations using text
    print('Matching user locations to congressional districts...')
    match_df = match_user_locations(sts_user_df, all_place_df)

    # 3. Add in geographic data and merge with congressional districts
    cd_places_df = spatial_join(all_place_df)

    # 4. Do sentiment analysis
    print('Analyzing constituent tweets...')
    sts_df = process_loc_sts(sts_tweet_df, match_df, cd_places_df)
    all_df = process_geo_all(all_tweet_df, cd_places_df)

    # 5. Aggregate data and export CSV
    final_df = all_df.merge(sts_df, on='GEOID', how='left')
    final_df.to_csv(CSV_PATH, index=False)
    print('Exported CSV with constituent tweet results.')


if __name__ == "__main__":
    go()
