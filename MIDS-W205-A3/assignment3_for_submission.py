#W205.3 - Al Byun
#Assignment 3

import pymongo
import pandas as pd
from boto.s3.connection import S3Connection
import nltk
import numpy as np
import matplotlib.pyplot as plt
import tweepy
import time
import datetime
import os
import subprocess
import zipfile
import csv
import re

# AWS
AWS_KEY = ''
AWS_SECRET = ''
# Twitter
consumer_key = "";
consumer_secret = "";
access_token = "";
access_token_secret = "";

#############################################################################
"""                    SECTION 1 - STORING TASKS                         """
#1-Storing Tasks

#1.1- Write a python program to automatically retrieve and store the JSON files 
# (associated with the tweets that include #NBAFinals2015 hashtag and the tweets
# that include #Warriors hashtag) returned by the twitter REST api in a MongoDB 
# database called db_restT.

#1.2- Write a python program to insert the chucked tweets associated with 
# the #NBAFinals2015 hashtag and the tweets associated with the #Warriors hashtag
# that you have gathered in the assignment 2 and stored on S3 to a MongoDB database
# called db_tweets. This program should pull the inputs automatically from your S3 
# buckets holding the chuncked tweets and insert them into the db_tweets.

conn = S3Connection(AWS_KEY, AWS_SECRET)

dbclient=pymongo.MongoClient()
db = dbclient['db_assignment3']
coll_tweet = db['db_restT']
coll = db['db_tweets']

#bucketname1 = 'june7_14_warriors_tweets'
bucketname1 = 'june7_14_nbafinals2015_tweets'
#bucketname1 = 'test-tweets-ab'

bucket = conn.get_bucket(bucketname1)
for file_key in bucket.list():
    contents = file_key.get_contents_as_string()
    content_lines = contents.split('\n')
    json_data = pd.read_json(contents)
    text = json_data[[u'text']]
    created_at = json_data[[u'created_at']]
    retweet_count = json_data[[u'retweet_count']] 
    screen_name, location, followers_count = [], [], [] 
    
    # Parse out JSON data and add it to the MongoDB databases
    for i in range(0,len(json_data)):
        #1.1 - Add entire json tweet data into db_restT
        coll_tweet.insert({"tweet":content_lines[i]})
        
        #1.2 - Add tweet data files into db_tweet
        screen_name.append(json_data[u'user'][i][u'screen_name'])
        location.append(json_data[u'user'][i][u'location'])
        followers_count.append(json_data[u'user'][i][u'followers_count'])
        coll.insert({"text":text['text'][i],"created_at":created_at['created_at'][i],"screen_name":screen_name[i], "location":location[i], "followers_count":followers_count[i], "retweet_count":int(retweet_count['retweet_count'][i])})


#############################################################################
"""        SECTION 2 - RETRIEVING AND ANALYZING TASKS                     """
#2-Retrieving and Analyzing Tasks

#2.1- Analyze the tweets stored in db_tweets by finding the top 30 retweets as 
# well as their associated usernames (users authored them) and the locations of users.
    
top_retweets = coll.find({u'retweet_count':{'$gt':0}}, {u'retweet_count':1,u'screen_name':1,u'location':1}).sort(u'retweet_count', pymongo.DESCENDING)
top_retweet_name = []
for j in range(0,30):
    top_retweet_name.append(top_retweets[j][u'screen_name'])


#2.2- Compute the lexical diversity of the texts of the tweets for each of the 
# users in db_restT and store the results back to Mongodb. To compute the lexical 
# diversity of a user, you need to find all the tweets of a particular user (a 
# user's tweets corpus), find the number of unique words in the user's tweets corpus, 
# and divide that number by the total number of words in the user's tweets corpus.
# You need to create a collection with appropriate structure for storing the results 
# of your analysis.

coll_lex = db['db_lexical']

### my database had 27,962 unique screen_names for 37,800 tweets
tweet_lex_screen_names = coll.find().distinct(u'screen_name')
tweet_lex = coll.find().sort(u'screen_name', pymongo.ASCENDING)
token_screen_name = {}

for screen_name in tweet_lex_screen_names:
    token_text = []  
    tweet_text = coll.find({u'screen_name':screen_name})
    for rec in tweet_text:
        tokens = nltk.word_tokenize(rec[u'text'])
        for i in range(0,len(tokens)):
            token_text.append(tokens[i])

    token_screen_name[screen_name] = token_text
    token_text_lower = [e.lower() for e in token_text]
    num_unique_words = len(nltk.FreqDist(token_text_lower))
    lexical_diversity = float(num_unique_words) / len(token_screen_name[screen_name])
    coll_lex.insert({u'screen_name':screen_name,u'corpus':token_screen_name[screen_name],u'num_unique_words': num_unique_words,u'lexical_diversity':lexical_diversity})

# plot of your lexical diversities in task 2.2 showing the lexical diveristies of the top 30 users            

# find top 30 users based on followers count
top_user = coll.find({u'followers_count':{'$gt':0}}, {u'followers_count':1,u'screen_name':1}).sort(u'followers_count', pymongo.DESCENDING)
top_user_name = []
for rec in top_user:
    if rec[u'screen_name'] in top_user_name:
        pass
    else:
        top_user_name.append(rec[u'screen_name'])

top_30_user_names = []
for i in range(0,30):
    top_30_user_names.append(top_user_name[i])

top_lexical_diversity = []
for screen_name in top_30_user_names:
    name_data = coll_lex.find({u'screen_name':screen_name})
    for rec in name_data:
        top_lexical_diversity.append(rec[u'lexical_diversity'])

# create the plot
index = np.arange(len(top_30_user_names))
plt.bar(index, top_lexical_diversity)
plt.xticks(index, top_30_user_names, rotation=30)
plt.xlabel('Top 30 Users (by Followers Count)')
plt.ylabel('Lexical Diversity')
plt.title('Lexical Diversity of Top 30 Users in Tweets Containing #Warriors/#NBAFinals2015 (7-14 June 2015)')
plt.show()

# design decision: include stop words (because it will normalize over all of the screen names, ie. all screen names have the same ones) and 
# allow the tokenizer to break up links (http://...) because it will also be normalized


#2.3- Write a python program to create a db called db_followers that stores all the 
# followers for all the users that you find in task 2.1. Then, write a program to 
# find the un-followed friends after a week for the top 10 users( users that have 
# the highest number of followers in task 2.1) since the time that you extracted 
# the tweets. In other words, you need to look for the people following the top 
# 10 users at time X (the time that you extracted the tweets) and then look at the 
# people following the same top 10 users at a later time Y (one-week after X) to 
# see who stopped following the top 10 users.

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth_handler=auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)

coll_followers = db['db_followers']

### Design decision: I chose to cap the number of followers stored to 10,000.
### Retrieving millions of followers would have taken over a week of time on my machine and set up

## top_30_user_names: u'MTVNews',u'MCHammer',u'globoesportecom',u'iloveruffag',u'htTweets',u'diarioas',u'FOXSports',u'GettySport',u'IndianExpress',u'warriors',u'Espngreeny',u'Rachel__Nichols',u'Diario_Libre',u'thehill',u'fanatikcomtr',u'CDN37',u'zaibatsu',u'danielbru',u'laureenmuy',u'Telediariogt',u'STcom',u'NBCSports',u'tuttosport',u'theage',u'sportschau',u'AlyssaValdez2',u'IAMPHILLYCHASE',u'primerahora',u'ABC7',u'ClaroRD'
for s_name in top_30_user_names:
    followers_list = []

    cursor_user = tweepy.Cursor(api.followers, screen_name=s_name,count=200).items(10000)
    while True:
        try:
            user = cursor_user.next() 
            followers_list.append(user.screen_name)   
        except tweepy.TweepError as e:
            print 'We got an exception ... Sleeping for 15 minutes'
            time.sleep(15*60)
            continue
        except StopIteration:
            break
                      
    coll_followers.insert({u'screen_name':s_name,u'followers_list':followers_list})


#find un-followed friends after a week for the top 10 users
# top_10_user_names: u'MTVNews',u'MCHammer',u'globoesportecom',u'iloveruffag',u'htTweets',u'diarioas',u'FOXSports',u'GettySport',u'IndianExpress',u'warriors'
top_10_user_names = []
for i in range(0,10):
    top_10_user_names.append(top_30_user_names[i])

followers_list_10 = {}
for screen_name in top_10_user_names:
    rec1 = coll_followers.find({u'screen_name':screen_name})
    for data in rec1:
        followers_list_10[data[u'screen_name']]=data[u'followers_list']

#old data collected for comparison 16-17 Jul 2015
followers_list_10_old = followers_list_10    
           
# collect new followers data for comparison 18-19 Jul 2015
# store this data in a separate MongoDB database (assignment instructions did not require an update to the existing database)
coll_followers_new_10 = db['db_followers_new_10']
for s_name in top_10_user_names:
    followers_list = []

    cursor_user = tweepy.Cursor(api.followers, screen_name=s_name,count=200).items(10000)
    while True:
        try:
            user = cursor_user.next() 
            followers_list.append(user.screen_name)   
        except tweepy.TweepError as e:
            print 'We got an exception ... Sleeping for 15 minutes'
            time.sleep(15*60)
            continue
        except StopIteration:
            break

    coll_followers_new_10.insert({u'screen_name':s_name,u'followers_list':followers_list})
            
followers_list_10_new = {}              #need to run this part starting here ################################################################3
for screen_name in top_10_user_names:
    rec1 = coll_followers_new_10.find({u'screen_name':screen_name})
    for data in rec1:
        followers_list_10_new[data[u'screen_name']]=data[u'followers_list']

# compare lists to find un-followed friends after a week for the top 10 users
### compare followers_list_10_old (16-17 Jul) versus followers_list_10_new (18-19 Jul) to see who dropped off
dropped_follower_list_10 = {}
for s_name3 in top_10_user_names:
    dropped_follower_list_10[s_name3] = list(set(followers_list_10_old[s_name3]) - set(followers_list_10_new[s_name3]))

writer = csv.writer(open('dropped_follower_list_10.csv', 'wb'))
for key, value in dropped_follower_list_10.items():
   writer.writerow([key, value])

"""
# to read in csv
reader = csv.reader(open('dropped_follower_list_10.csv', 'rb'))
dropped_follower_list_10 = dict(x for x in reader)
"""

#2.4- .(Bonus task) Write a python program and use NLTK to analyze the top 30 retweets 
# of task 2.1 as positive or negative (sentiment analysis). This is the bonus part
# of the assignment.

#############################################################################
"""                    CODE TO TRAIN CLASSIFIER                         """
# adapted from http://ravikiranj.net/posts/2012/code/how-build-twitter-sentiment-analyzer/

#start process_tweet
def processTweet(tweet):
    #Convert to lower case
    tweet = tweet.lower()
    #Convert www.* or https?://* to URL
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','URL',tweet)
    #Convert @username to AT_USER
    tweet = re.sub('@[^\s]+','AT_USER',tweet)
    #Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    #Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    #trim
    tweet = tweet.strip('\'"')
    return tweet
#end

#start replaceTwoOrMore
def replaceTwoOrMore(s):
    #look for 2 or more repetitions of character and replace with the character itself
    pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
    return pattern.sub(r"\1\1", s)
#end

#start getfeatureVector
def getFeatureVector(tweet):
    featureVector = []
    #split tweet into words
    words = tweet.split()
    for w in words:
        #replace two or more with two occurrences
        w = replaceTwoOrMore(w)
        #strip punctuation
        w = w.strip('\'"?,.')
        #check if the word stats with an alphabet
        val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*$", w)
        #ignore if it is a stop word
        stopWords = nltk.corpus.stopwords.words('english')
        stopWords = stopWords + ['URL','AT_USER']       
        if(w in stopWords or val is None):
            continue
        else:
            featureVector.append(w.lower())
    return featureVector
#end

#Read the training tweets and process them
inpTweets = csv.reader(open('C:\\Users\\Albert\\Desktop\\github\\Assignment3\\full_training_dataset.csv', 'rU'), delimiter=',', quotechar='|')
featureList = []

tweets = []
count = 1
for row in inpTweets:
    sentiment = row[0]
    if sentiment == 'negative' or sentiment == 'positive':
        tweet = row[1]
    else:
        tweet = ''
        sentiment = 'neutral'
    processedTweet = processTweet(tweet)
    featureVector = getFeatureVector(processedTweet)
    featureList.extend(featureVector)
    tweets.append((featureVector, sentiment));
    count += 1
#end loop

# Remove featureList duplicates
featureList = list(set(featureList))

#start extract_features
def extract_features(tweet):
    tweet_words = set(tweet)
    features = {}
    for word in featureList:
        features['contains(%s)' % word] = (word in tweet_words)
    return features
#end

# Extract feature vector for all training tweets
training_set = nltk.classify.util.apply_features(extract_features, tweets)

"""                END OF CODE TO TRAIN CLASSIFIER                     """
#############################################################################

# find tweets for top 30 retweets
top_retweets_sent = coll.find({u'retweet_count':{'$gt':0}}, {u'retweet_count':1,u'screen_name':1,u'text':1}).sort(u'retweet_count', pymongo.DESCENDING)
top_retweet_name = []
top_retweet_count = []
top_retweet_text = []
for j in range(0,30):
    top_retweet_name.append(top_retweets_sent[j][u'screen_name'])
    top_retweet_count.append(top_retweets_sent[j][u'retweet_count'])
    top_retweet_text.append(top_retweets_sent[j][u'text'])

# Train the classifier
NBClassifier = nltk.NaiveBayesClassifier.train(training_set)

# Test the classifier
top_retweet_sentiment = []
for tweet in top_retweet_text:
    processedTestTweet = processTweet(tweet)
    sentiment = NBClassifier.classify(extract_features(getFeatureVector(processedTestTweet)))
    top_retweet_sentiment.append(sentiment)

# Create tuple of tweet, retweet_count, and sentiment and export to a CSV file
for i in range(0,len(top_retweet_text)):
    top_retweet_text[i] = top_retweet_text[i].encode('ASCII', 'ignore')

results = zip(top_retweet_sentiment,top_retweet_text,top_retweet_count)

with open('sentiment_analysis_top_30_retweets.csv','w') as out:
    csv_out=csv.writer(out)
    csv_out.writerow(['Sentiment','Top_30_Retweet','Retweet_Count'])
    for row in results:        
        csv_out.writerow(row)


#############################################################################
"""          SECTION 3 - STORING AND RETRIEVING TASKS                     """
#3-Storing and Retrieving Task

#3.1- Write a python program to create and store the backups of both db_tweets and
# db_restT to S3. It also should have a capability of loading the backups if necessary.

#code adapted from http://blog.matt-swain.com/post/36316268866/simple-versioned-backups-for-mongodb

collections = db.collection_names() ## need to update these paths for my case
database = 'db_assignment3'
#backup_path = '/c/users/albert/Documents/mongobackup/'
#mongoexport_path = '/c/MongoDB/bin/mongodump'
#mongoimport_path = '/c/MongoDB/bin/mongorestore'
backup_path = "C:\\Users\\Albert\\Documents\\mongobackup\\"
restore_path  = "C:\\Users\\Albert\\Documents\\mongobackup\\restore_files\\"
mongoexport_path = "C:\\MongoDB\\bin\\mongodump"
mongoimport_path = "C:\\MongoDB\\bin\\mongorestore"

def run_backup():
    """ Export each collection to a file, hard link duplicates and delete old backups """

    # Set up new backup folder
    now = datetime.datetime.today().strftime('%Y%m%d-%H%M%S')
    this_backup = os.path.join(backup_path, now)
    os.mkdir(this_backup)
    print('Created new backup: %s' % this_backup)

    # Save compressed collections to folder
    # The assignment instructions only called for backing up db_tweets and db_restT, but 
    # this code errors on the side of caution and backs up all collections in the database
    for collection in collections:
        print('mongoexport: %s' % collection)
        filepath = os.path.join(this_backup, collection)
        subprocess.call([mongoexport_path, '--host', 'localhost', '--port', '27017', '--db', database, '--collection', collection, '--out', filepath+'.json'])        
        myZip = zipfile.ZipFile(filepath+'.zip', 'w', zipfile.ZIP_DEFLATED, True)
        for root, dirs, files in os.walk(filepath+'.json'):
            for file in files:
                myZip.write(os.path.join(root, file))
        myZip.close()
        #os.remove(filepath+'.json')
  
    # Move backup files to S3 folder
    bucket = conn.create_bucket('w205_assignment3_mongodb')

    from boto.s3.key import Key

    for file in os.listdir(this_backup):
        if file.endswith(".zip"):
            myKey = Key(bucket)
            myKey.key = file
            myKey.set_contents_from_filename(this_backup+'\\'+file)
            myKey.make_public()

run_backup()


def restore_backup(collection):
    # Pull the mongodb files to S3 bucket 
    bucket = conn.get_bucket('w205_assignment3_mongodb')
    from boto.s3.key import Key
    
    bucket_list = bucket.list()
    for l in bucket_list:
        keyString = str(l.key)
        # check if file exists locally, if not: download it
        if not os.path.exists(backup_path+keyString):
            l.get_contents_to_filename(backup_path+keyString)     
            
    """ Restore a collection from the collection backup """
    zippath = os.path.join(restore_path,'%s.zip' % collection)
    z = zipfile.ZipFile(zippath)
    with zipfile.ZipFile(zippath, "r") as z:
        z.extractall(restore_path + '\\' + collection)
    collection_file_path = ''
    for root, dirs, files in os.walk(restore_path + '\\' + collection):
        for file in files:
            print root
            root = collection_file_path
    db[collection].rename('%s_old' % collection)
    subprocess.call([mongoimport_path, '--db', database, '--collection', collection, collection_file_path])
    #os.remove(jsonpath)

restore_backup('db_tweets')