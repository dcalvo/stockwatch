import datetime
import tweepy
import os

auth = tweepy.OAuthHandler(os.environ["consumer_key"], os.environ["consumer_secret"])

api = tweepy.API(auth)

tweets = api.search_tweets("AMC", lang="en", count=10)

count = 0
for tweet in tweets:
    if hasattr(tweet, "retweeted_status"):
        count += 1
        print(tweet.retweeted_status.id)
print(count)

today = datetime.datetime.today()
one_week_ago = today - datetime.timedelta(days=7)

print(today.strftime("%Y-%m-%d"), one_week_ago.strftime("%Y-%m-%d"))
