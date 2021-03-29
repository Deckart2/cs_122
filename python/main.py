import sys
import process_constituent_tweets
import reps_sentiment
import combine_files


def get_user_input():
    '''
    Asks user whether or not they want to call all intermediate modules.
    '''
    print("\n----2020 Election Analysis----")
    print("\nDo you want to run all intermediate modules?")
    print("\nEnter Yes to go through all intermediate analysis.")
    print("\nEnter No to open website with final visualization.")
    run_analysis = input("\nEnter (Y/N): ")
    return run_analysis


def get_int_user_input():
    '''
    Asks user whether or not they want to query the twitter API for the Rep data.
    '''
    print("\n----Sentiment Analysis and Keywords of US Representatives")
    print("\nDo you want to conduct this analysis? It will query the Twitter API to form the csv.")
    print("\nIf so, buckle up! This process takes about 40 minutes.")
    print("\nEnter Yes to go through the process.")
    print("\nEnter No to move on to the districts file processing.")
    response = input("\nEnter (Y/N): ")
    return response


def analyze_twitter_reps():   
    '''
    Based on input from user, either calls twitter api to get representatives'
    tweets, or moves on.
    '''
    response = get_int_user_input()
    if response == 'Y':
        reps_sentiment.create_csv()
    elif response == 'N':
        print("Most recent generated csv is in generated_data, titled Aggregated_Twitter_Rep_Data.csv")
        print("Moving on to the district file processing.")
        print('''If you want to try a single df, you can run reps_sentiment.get_df(state, district) 
        with state abbreviation and district number as strings, ex.('TX', '1')''')
    else:
        print("Invalid entry, try again.")
        analyze_twitter_reps()


def do_all_intermediate_steps():
    '''
    Analyze and aggregate all data.
    '''
    print("Beginning analysis...")

    # Analyze all constituent tweets and export csv
    process_constituent_tweets.go()

    # Analyze twitter reps pending user input
    analyze_twitter_reps()

    # Add propublica data and create final input file to website
    combine_files.write_districts()


def go():
    '''
    Main function to get user input and run intermediate analyses
    '''
    run_analysis = get_user_input()
    if run_analysis == 'Y':
        do_all_intermediate_steps()
    elif run_analysis == 'N':
        print('Opening website...')
    else:
        print('''Incorrect entry. Enter "Y" or "N".''')
        go()


if __name__ == "__main__":
    go()
