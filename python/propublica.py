#Use the Propublica API to access Representatives' Votes
'''
    This script 
'''


import numpy as np
import pandas as pd
import requests
import os
import json
import geopandas
import keys 

propublica_api = keys.propublica_api

def get_roll_call(chamber, congress_number, session_number, 
                  roll_call_number):
    '''
    A relatively targetted function that returns 
        how either all Representatives or Senators voted
        on a rollcall votes using the Propublica API
    Inputs:
        congress_number (int): the current "iteration of Congress"
            ex: the 2021 congress_number is 117 (ie the 117th Congress)
            Note that propublica can only handle requests for votes from:
                102-117 sessions for the House
                101-117 sessions for the Senate
        chamber (string): either "house" or "senate", specifying the 
            chamber whose data will be returned
        session_number (int): either 1 or 2. 1 for if vote took place 
            in an odd year, 2 if it took place in an even year
        roll_call_number (int): the number of the vote
    Outputs:
        (1) a .json file in the propublica_data folder with the data returned 
            from the api. This file's nameing convention is:
                chamber_congress_number_session_number_roll_call_number.json
        (2) a pandas df of the json data (which recieves minor transformations)
    
    Note:
        os guidance for os.system() and writing to a file https://stackoverflow.com/questions/89228/how-to-execute-a-program-or-call-a-system-command-from-python
        general requests: https://2.python-requests.org/en/master/user/quickstart/#make-a-request
        Reading json help: https://www.geeksforgeeks.org/read-json-file-using-python/
        For column merging
    '''

    url = ("https://api.propublica.org/congress/v1/" + str(congress_number) +
        "/" + chamber + "/sessions/" + str(session_number) + 
        "/votes/" + str(roll_call_number) + ".json")
    header = "X-API-Key: " + propublica_api
    f_name = ("generated_data/propublica_data/" + chamber + "_" + str(congress_number) 
            + "_" + str(session_number) + "_" + str(roll_call_number) + ".json")
    vote_name = "vote_" + str(roll_call_number)
    
    f_directions =  "> "  + f_name

    command = str('curl ' + "'" + url + "'" + ' -H ' + "'" + header + "'" + f_directions)
    os.system(command)
    data_json = open(f_name)
    data = json.load(data_json)
    sub_data = data["results"]["votes"]["vote"]["positions"]
    data_pd = (pd.json_normalize(sub_data)
                 .loc[:, ["member_id", "name", "party", "state", 
                    "district", "vote_position"]]
                 .rename(columns = {"vote_position" : vote_name}))
    data_pd.district = data_pd.district.str.zfill(2)
 
    return data_pd

def classify_democratic(votes):
    '''
    Function that adds a column to the districts dataframe that classifies
        each representative as democratic, anti-democractic, or mixed
            democratic- upheld AZ's and PA's 2020 election results and 
                voted to impeach Trump
            anti-democratic- voted not to uphold AZ's and PA's 2020 election
                results and voted not to impeach Trump
            mixed- neither democratic or anti-democratic
    Inputs: 
        votes: the df created in the compute_output function
    Outputs:
        votes but with an updated column called "vote_summary" with the 
            classifications described above
    Classification code followed:
                https://www.dataquest.io/blog/tutorial-add-column-pandas-dataframe-based-on-if-else-condition/
    '''

    conditions = [
        (votes["vote_17"] == "Yes") & (votes["vote_10"] == "No") 
        & (votes["vote_11"] == "No"),
        (votes["vote_17"] == "No") & (votes["vote_10"] == "Yes") &
        (votes["vote_11"] == "Yes")]
    classification = ["democractic", "anti_democratic"]
    votes["vote_summary"] = np.select(conditions, classification, default="mixed")

    return votes


def compute_output():
    '''
    Function that runs the above function to get three votes and combines that
        data with other district data to allow for future joins
    Input: 
        propublica_api- the propublica api key
    Outputs:
        This function does not return anything but writes the to a csv 
            called propublica_district_data.csv in the generated_data folder
    
    Notes:
        Two representatives do not appear in propublica, so we do not 
        have their votes:
            NY District 22: 
                See: https://ballotpedia.org/New_York%27s_22nd_Congressional_District
            LA District 05: 
                See: https://ballotpedia.org/New_York%27s_22nd_Congressional_District_election,_2020
    '''
    #Read in a Census Text File to match state names to numbers 
    state_names = pd.read_csv("static_data/congressional_districts_reference/state_reference.txt", 
    sep = "|", dtype="str")
    state_names.STATE = state_names.STATE.str.zfill(2)
    state_names = (state_names.rename(columns={
                                            "STATE":"state_num",
                                            "STATE_NAME":"state_name",
                                            "STUSAB":"state"})
                            .drop("STATENS", axis=1))
    #Read in shapefile to get geoid to match:
    districts = (geopandas.read_file("static_data/congressional_districts/cb_2019_us_cd116_500k.shp")
                .rename(columns = {"CD116FP":"district",
                                "STATEFP":"state_num"}))
    districts = districts[~districts.state_num.isin(["60", "66", "69", "72",
            "74", "78", "11"])]
    districts.district.replace("00", "01", inplace = True)

    #Use function to get pd dfs for the three votes and then combine them
    print("Reading AZ votes...")
    az_vote = get_roll_call("house", 117, 1, 10)
    print("Reading PA votes...")
    pe_vote = get_roll_call("house", 117, 1, 11)
    print("Reading Impeachment votes...")
    trump_vote = get_roll_call("house", 117, 1, 17)

    votes = (pd.merge(trump_vote, az_vote[["member_id", "vote_10"]], 
                    how = "outer",
                    on = "member_id")
            .merge(pe_vote[["member_id", "vote_11"]], 
                    how = "outer",
                    on = "member_id")
            .merge(state_names,
                    how = "left", on = "state")
                .merge(districts[['state_num', 'district', 'GEOID']],
                    how = "right", on=['state_num', 'district']))

    #Classify democratic/anti-democratic or mixed:
    votes = classify_democratic(votes)
    votes.to_csv("generated_data/propublica_district_data.csv")

#compute_output(propublica_api)

if __name__ == "__main__":
    compute_output()