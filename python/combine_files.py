#File to combine all data into one Geodataframe
'''
    This script performs the following operations:
        (1) Reads in propublica, twitter representative, twitter constituents
            and district spatial data
        (2) Combines them to one dataframe and creates a column to compare
            representatives and constituents
        (3) Changes the geographic locations of Alaska and Hawaii
        (4) Writes to a shapefile for visualization
'''

import pandas as pd
import geopandas

def read_and_merge_data():
    '''
    Function that reads propublica, two sources of twitter data and spatial data
        and combines them 
    Inputs: nothing, function takes data from other files
    Output: districts (geodataframe): a combined geodataframe with all data
    
    Note:
        Lowercase code help from: https://cmdlinetips.com/2020/07/cleaning_up_pandas-column-names/
    '''

    district_data = pd.read_csv("../generated_data/propublica_district_data.csv",
                                dtype={"GEOID":"str",
                                    "state_num":"str",
                                    "district":"str"})
    shp_source = "../static_data/congressional_districts/cb_2019_us_cd116_500k.shp"
    district_shp = geopandas.read_file(shp_source)
    district_shp = district_shp[["GEOID", "geometry"]]

    twitter_geo = pd.read_csv("../generated_data/twitter_constituent_data.csv",
        dtype={"GEOID":"str"})

    twitter_rep = pd.read_csv("../generated_data/Aggregated_Twitter_Rep_Data.csv",
                            dtype={"District":"str"})
    twitter_rep.District = twitter_rep.District.str.zfill(2)
    twitter_rep.columns = twitter_rep.columns.str.lower()
    twitter_rep.district.replace("00", "01", inplace=True)

    districts = (pd.merge(district_shp, district_data, how = "right", on = "GEOID")
                .drop(columns = ["Unnamed: 0"])
                .merge(twitter_geo, how="left", on="GEOID")
                .merge(twitter_rep, how = "left", on=["state", "district"]))

    districts["mean_dif_subjectivity_all"] = (
        districts["mean_subjectivity"] - districts["avg_subjectivity_geo_all"])

    print("combining twitter and propublica data...")
    return districts

def change_geography():
    '''
    Resizes and moves Alaska and moves Hawaii so that they fit ear
        the continental USA
    Input: the districts geodataframe used above
    Output: 
        No function output but it does update the districts geodataframe
            geography attributes and writes the file to the generated data 
            folder
    
    Notes:
    The general structure of this code follows the following two links
        https://www.storybench.org/how-to-shift-alaska-and-hawaii-below-the-lower-48-for-your-interactive-choropleth-map/
        https://rstudio-pubs-static.s3.amazonaws.com/94122_462a1d171e4944f0a99c1f91fd5071d5.html#move-alaska-scaled-down-and-hawaii
        This code was all original because their work was in R
    Indexing syntax from: https://stackoverflow.com/questions/40095632/replacing-values-in-a-column-for-a-subset-of-rows
    '''
    districts = read_and_merge_data()
    districts = districts.to_crs("+proj=laea +lat_0=45 +lon_0=-100 +x_0=0 \
    +y_0=0 +a=6370997 +b=6370997 +units=m +no_defs")
    
    alaska_geo = districts[districts.state_name.isin(["Alaska"])]
    alaska_geo = alaska_geo.scale(xfact=.43, yfact=.43, origin=(0, 0))
    alaska_geo = alaska_geo.translate(xoff=-800000, yoff=-3100000) 

    hawaii_geo = districts[districts.state_name.isin(["Hawaii"])]
    hawaii_geo = hawaii_geo.translate(xoff=4500000, yoff=-1200000)

    indexer_al = districts[districts.state_name == "Alaska"].index
    indexer_hi = districts[districts.state_name == "Hawaii"].index
    districts.loc[indexer_al, 'geometry'] = alaska_geo
    districts.loc[indexer_hi, 'geometry'] = hawaii_geo
    
    print("Resizing Alaska and Hawaii...")
    return districts
    
def write_districts():
    '''
    Function that takes districts and writes it
    Inputs: None
    Output:
        No function output but writes districts data into the
            generated_data folder 
    '''
    districts = change_geography()
    districts.to_file("../generated_data/districts1.shp")
    print("Writing to shapefile...")


if __name__ == "__main__":
    write_districts()