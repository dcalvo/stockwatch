import os
from datetime import datetime, timedelta

import tweepy

# What are we looking up?
search_query = "AMC"

# How many unique Tweets do we collect for each day?
tweets_per_day = 10000

# Today and one week ago in YYYY-MM-DD
today = datetime.today().strftime("%Y-%m-%d")
one_week_ago = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")

# Authenticate and launch Tweepy with rate limiting (450rqs / 15min allegedly)
auth = tweepy.OAuthHandler(os.environ["consumer_key"], os.environ["consumer_secret"])
api = tweepy.API(auth, wait_on_rate_limit=True)

# Initiate a search with 100 items per page in English
tweets = tweepy.Cursor(api.search_tweets, search_query, lang="en", count=100)

retweeted = 0
for count, tweet in enumerate(tweets.items(5)):
    if hasattr(tweet, "retweeted_status"):
        retweeted += 1
        print(tweet.retweeted_status.id)
print(f"Total: {count+1} | Unique: {count-retweeted+1} | Retweets: {retweeted}")

# Take 1 day time slices of a trading week.
# Collect 10k unique Tweets (`tweet.retweed_status`) per time slice.
# Collect sentiment scores for each Tweet. Multiply sentiment score by retweets (floor 1).
