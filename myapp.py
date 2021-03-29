from python.graph_script import (tweet_count,user_count,vote_summary, 
                                 positive_reps, negative_reps, reps_vs_constituents)
from flask import Flask, render_template,request
import json
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.embed import json_item

app = Flask(__name__)

@app.route('/')
def home():
    # Total tweets
    p1 = tweet_count("#StopTheSteal Tweet Counts by Congressional District")
    
    # Unique users
    p2 = user_count("#StopTheSteal Unique Users by Congressional District")
    
    # Vote summmary
    p3 = vote_summary("Vote Summary by Congressional District")
    
    # Positive % Reps
    p4 = positive_reps("Percentage of Positive Tweets by Representative")

    # Negative % Reps
    p5 = negative_reps("Percentage of Negative Tweets by Representative")
    
    # Difference between reps and constituents
    p6 = reps_vs_constituents("Difference in Subjectivity of Tweets between representatives and constituents")

    script1,plot_dict = components({"tweet_plot":p1,"user_plot":p2,"vote_plot":p3,"positive_plot":p4,
                                    "negative_plot":p5,"reps_vs_consts":p6})
    
    return render_template('index.html',script1=script1,plot_dict=plot_dict)

if __name__ == '__main__':
    app.debug = True
    app.run()
