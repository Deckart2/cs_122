#Common functions to conduct sentiment analysis of tweets

import pandas as pd
import numpy as np
import re
from datetime import datetime
from collections import Counter
from textblob import TextBlob

import string
from nltk.corpus import stopwords

eng_stopwords = stopwords.words('english')
characters = [s for s in string.printable]

STOP_WORDS = eng_stopwords + characters + ['&amp;']


def cleantwt(text): #cleaning tweets
    '''
    Returns cleaned text
    '''
    text = re.sub(r'@[A-Za-z0-9]+', '', text) #removes @ mentions
    text = re.sub(r'#', '', text) #removes hashtag symbols
    text = re.sub(r'RT[\s]+', '', text) #removing RTs
    text = re.sub(r'https?:\/\/\S+', '', text) #removes hyperlink

    return text


def subjectivity(text): #function to get subjectivity
    '''
    Returns subjectivity score of given text
    '''
    return TextBlob(text).sentiment.subjectivity


def polarity(text): #function to get polarity
    '''
    Returns polarity score of given text
    '''
    return TextBlob(text).sentiment.polarity


def analysis(score): #function to compute neg, neutral, pos analysis
    '''
    Returns an analysis of a given polarity score
    '''
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'


def get_keywords(df_column):
    '''
    Returns most common keywords from tweets not counting stop words
    '''
    most_common = Counter(" ".join(df_column.str.lower()).split()).most_common(40)
    keywords = []
    for tup in most_common:
        word, count = tup
        if word not in STOP_WORDS:
            keywords.append(tup)
    return keywords
