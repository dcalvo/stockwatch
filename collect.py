import os
import pickle
from datetime import datetime, timedelta

import tweepy
from tqdm import tqdm

# Authenticate and launch Tweepy with rate limiting (450rqs / 15min allegedly)
auth = tweepy.OAuthHandler(os.environ["consumer_key"], os.environ["consumer_secret"])
api = tweepy.API(auth, wait_on_rate_limit=True)

# What are we looking up?
search_query = "GME"

# How many unique Tweets do we collect for each day?
tweets_per_day = 10000

# Reporting?
verbose = True

# Variables to keep track of outside the loop
total_stats = {"total": 0, "unique": 0, "retweets": 0, "dict": 0, "dupes": 0}
yesterdays_latest_status = -1

# Track Tweets for a week, from beginning of 1 week ago to end of yesterday
for day in range(7, 0, -1):
    # Note `day-1` since the Twitter API only has a "before this date" parameter
    date = (datetime.today() - timedelta(days=day - 1)).strftime("%Y-%m-%d")

    # Initiate a search with 100 items per page in English
    tweets = tweepy.Cursor(
        api.search_tweets,
        search_query,
        lang="en",
        count=100,
        until=date,
        result_type="mixed",
        since_id=yesterdays_latest_status,
        tweet_mode="extended",
    )

    # Set to the date that's actually representative of the results
    date = (datetime.today() - timedelta(days=day)).strftime("%Y-%m-%d")

    # Create a hashmap of unique tweets where keys are status IDs and values are Tweet objects
    tweets_dict = {}

    # Populate the `tweets_dict` with up to `tweets_per_day` tweets
    retweeted = 0
    todays_latest_status = yesterdays_latest_status
    for count, tweet in tqdm(
        enumerate(tweets.items()),
        desc=f"Finding Tweets for {date}",
        total=tweets_per_day,
        leave=False,
    ):
        if hasattr(tweet, "retweeted_status"):
            if tweet.retweeted_status.id not in tweets_dict:
                tweets_dict[tweet.retweeted_status.id] = tweet.retweeted_status
                retweeted += 1
        else:
            if tweet.id not in tweets_dict:
                tweets_dict[tweet.id] = tweet

        if tweet.id > todays_latest_status:
            todays_latest_status = tweet.id

        if len(tweets_dict) == tweets_per_day:
            break

    # Update the oldest Tweet we'll collect
    yesterdays_latest_status = todays_latest_status

    # Save the day's tweets
    pickle.dump(tweets_dict, open(f"tweets_dict_{date}.pickle", "wb"))

    # Reporting metrics
    if verbose:
        print(f"=========={date}==========")
        print(
            f"Total: {count+1} | Unique: {count-retweeted+1} | Retweets: {retweeted} | Dict: {len(tweets_dict)} | Dupes: {count+1 - len(tweets_dict)}\n"
        )
    total_stats["total"] += count + 1
    total_stats["unique"] += count - retweeted + 1
    total_stats["retweets"] += retweeted
    total_stats["dict"] += len(tweets_dict)
    total_stats["dupes"] += count + 1 - len(tweets_dict)

print(
    f"=========={(datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')} to {datetime.today().strftime('%Y-%m-%d')}=========="
)
print(
    f"Total: {total_stats['total']} | Unique: {total_stats['unique']} | Retweets: {total_stats['retweets']} | Dict: {total_stats['dict']} | Dupes: {total_stats['dupes']}"
)

# tweets_dict = pickle.load(open("tweets_dict_2021-06-21.pickle", "rb"))
# for tweet in tweets_dict.values():
#     print(tweet.created_at)
#     print(tweet.retweet_count)
#     print(tweet.full_text)

# Take 1 day time slices of a trading week.
# Collect 10k unique Tweets (`tweet.retweed_status`) per time slice.
# Collect sentiment scores for each Tweet. Multiply sentiment score by retweets (floor 1).
