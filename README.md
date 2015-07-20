# MIDS-W205-A3

Storing, Retrieving, and Analyzing Social Media Data Using MongoDB Assignment
W205.3, Summer 2015

I- Design Decisions and Rationale

1-Storing Tasks

1.1- Write a python program to automatically retrieve and store the JSON files (associated with the tweets that include #NBAFinals2015 hashtag and the tweets that include #Warriors hashtag) returned by the twitter REST api in a MongoDB database called db_restT.
1.2- Write a python program to insert the chunked tweets associated with the #NBAFinals2015 hashtag and the tweets associated with the #Warriors hashtag that you have gathered in the assignment 2 and stored on S3 to a MongoDB database called db_tweets. This program should pull the inputs automatically from your S3 buckets holding the chunked tweets and insert them into the db_tweets.

I performed these two tasks in one for loop.
I pulled the chunks (text files) containing the json documents of tweets from Assignment 3. 
These tweets were pulled from two separate S3 buckets ("june7_14_warriors_tweets" and "june7_14_nbafinals2015_tweets").
As this for loop iterated over these chunks, each raw tweet json document, including metadata, was passed into the "db_restT" MongoDB collection.
Then the "text", "created_at", "screen_name", "location", "followers_count", and "retweet_count" were parsed out of each tweet json document and placed into the "db_tweets" MongoDB collection.


2-Retrieving and Analyzing Tasks

2.1- Analyze the tweets stored in db_tweets by finding the top 30 retweets as well as their associated usernames (users authored them) and the locations of users.

I performed this task by sorting the tweets in the "db_tweets" collection by "retweet_count", in descending order.
Then the "screen_name" and "location" fields for each were saved, along with the text.

2.2- Compute the lexical diversity of the texts of the tweets for each of the users in db_restT and store the results back to Mongodb. To compute the lexical diversity of a user, you need to find all the tweets of a particular user (a user's tweets corpus), find the number of unique words in the user's tweets corpus, and divide that number by the total number of words in the user's tweets corpus.
You need to create a collection with appropriate structure for storing the results of your analysis.

For this task, I created the "db_lexical" MongoDB collection, which stored fields for "screen_name", "corpus", "num_unique_words", and "lexical_diversity".
I sorted all the tweets in the "db_tweets" collection to find a unique list of "user_names".
Then I iterated through the "db_tweets" collection again to find all the tweets directly from a particular user and then I created a "corpus" by tokenizing the text.
I calculated the "lexical_diversity" for each by dividing the of unique words by the total number of words (or size of corpus).

I found the list of "Top 30 Users" based on the number of "followers_count" and I plotted the "lexical_diversity" of each in a bar graph, ordered by "followers_count".

2.3- Write a python program to create a db called db_followers that stores all the followers for all the users that you find in task 2.1. Then, write a program to find the un-followed friends after a week for the top 10 users( users that have the highest number of followers in task 2.1) since the time that you extracted the tweets. In other words, you need to look for the people following the top 10 users at time X (the time that you extracted the tweets) and then look at the people following the same top 10 users at a later time Y (one-week after X) to see who stopped following the top 10 users.

For this task, I created the MongoDB collection "db_followers".
I took the list of "Top 30 Users" and I iterated over each.
I used the Twitter followers API, with a count of 200 per call, and I found a list of 10,000 followers for each.
This data retrieval exercise was time and resource intensive, as it took me about 2 full days to collect this data (10,000 followers for each of the top 30 users).
I stored the "screen_name" and "followers_list" for each user into the "db_followers" collection.

Because it took me so long to collect this data, I could not wait the full 7 days specified in the assignment instructions to compare.
I waited about 2 days and I pulled 10,000 followers again using the same methodology for the "Top 10 Users".
I then compared the "followers_list_10_old" to the "followers_list_10_new" to see which followers were dropped during this time for each user.
I stored this data into the "dropped_follower_list_10.csv".
Each user had dropped over 1,000 followers over the 2 day period. The results may have been a little misleading because the 2 different data pulls may have retrieved different portions of the entire followers list for each user.

2.4- .(Bonus task) Write a python program and use NLTK to analyze the top 30 retweets of task 2.1 as positive or negative (sentiment analysis). This is the bonus part of the assignment.

I attempted this Bonus task by using NLTK NaiveBayesClassifier.
The Naive Bayes Classifier used the training tweet sentiment dataset found in "full_training_dataset.csv".
The script processed the tweets in this training data into a standard, usable format and then learned the sentence and word construct for "positive", "neutral", and "negative" text.
This Classifier was run on the "Top 30 Retweets" and the sentiment was approximated for each.
The "Top 30 Retweets" and each approximated sentiment were stored into the "sentiment_analysis_top_30_retweets.csv".


3-Storing and Retrieving Task

3.1- Write a python program to create and store the backups of both db_tweets and db_restT to S3. It also should have a capability of loading the backups if necessary.

I completed this task using MongoDump to create the backups.
I ran the MongoDump script on each collection of the database, and then zipped the json and bson files into a .zip file.
Each collection had a .zip file with its respective json and bson files.
These .zip files were uploaded into an S3 bucket called "w205_assignment3_mongodb".

I completed the restore task by using MongoRestore.
The .zip files were downloaded from S3, unzipped, put into a folder, and re-mapped to MongoDB.


Deliverables

1- A link to your S3 bucket that holds the backups documented in your README.md file. Make sure to make it publicly accessible.

My S3 buck with my MongoDB backups are located here:
https://console.aws.amazon.com/s3/home?region=us-west-2#&bucket=w205_assignment3_mongodb&prefix=

2- Your python codes.

"assignment3_for_submission.py" - is a single script with my solution for each of the tasks above
The "for_submission" version is a duplicate of my running version, except the access keys and tokens were removed.

3- The plot of your lexical diversities in task 2.2 showing the lexical diveristies of the top 30 users and the result of the sentiment analysis in task 2.4 if you complete the bonus part.

"figure_1.png" - contains my plot of lexical diversities from task 2.2
"dropped_follower_list_10.csv" - contains the results from task 2.3, the difference between the "followers_list_10_old" and the "followers_list_10_new"
"sentiment_analysis_top_30_retweets.csv" - contains the result of my sentiment analysis for the Top 30 Retweets using the Naive Bayes Classifier
"full_training_dataset.csv" - contains the training data used to train the Naive Bayes Classifier
