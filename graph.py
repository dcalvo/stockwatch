from csv import reader
import numpy as np
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


def get_sentiment_scores(date):
    with open(f"tweets_sentiment_{date}.csv", "r", encoding="utf-8") as f:
        csv_reader = reader(f)

        # columns = [Text, Retweets, Negative, Neutral, Positive]
        labels = ["negative", "neutral", "positive"]
        columns = next(csv_reader)

        sentiment_dict = {"negative": [], "neutral": [], "positive": []}
        for row in csv_reader:
            if row:
                text, retweet_count, negative_score, neutral_score, positive_score = (
                    row[0],
                    int(row[1]),
                    float(row[2]),
                    float(row[3]),
                    float(row[4]),
                )

                # Set the sentiment classification as the highest sentiment score
                sentiment_direction = labels[
                    np.argmax([negative_score, neutral_score, positive_score])
                ]
                sentiment_score = max(negative_score, neutral_score, positive_score)

                weighted_sentiment = 0
                if retweet_count:
                    weighted_sentiment = retweet_count * sentiment_score
                else:
                    # Tweet has no Retweets, give it weight of 1
                    weighted_sentiment = 1 * sentiment_score

                sentiment_dict[sentiment_direction] += [math.ceil(weighted_sentiment)]

    return sentiment_dict


def get_data_series():
    sentiment_dicts = []
    dates = []
    for day in range(7, 0, -1):
        date = (datetime.today() - timedelta(days=day)).strftime("%Y-%m-%d")
        dates += [(datetime.today() - timedelta(days=day)).strftime("%m-%d")]
        sentiment_dicts += [get_sentiment_scores(date)]

    # print(sentiment_dicts)

    daily_negative_sentiment = []
    daily_neutral_sentiment = []
    daily_positive_sentiment = []
    for sentiment_dict in sentiment_dicts:
        daily_negative_sentiment += [math.ceil(np.average(sentiment_dict["negative"]))]
        daily_neutral_sentiment += [math.ceil(np.average(sentiment_dict["neutral"]))]
        daily_positive_sentiment += [math.ceil(np.average(sentiment_dict["positive"]))]

    return (
        dates,
        daily_negative_sentiment,
        daily_neutral_sentiment,
        daily_positive_sentiment,
    )


def plot(
    title,
    dates,
    daily_negative_sentiment,
    daily_neutral_sentiment,
    daily_positive_sentiment,
):
    plt.plot(dates, daily_negative_sentiment, color="red", marker="v", label="Negative")
    plt.plot(dates, daily_neutral_sentiment, color="blue", marker="_", label="Neutral")
    plt.plot(
        dates, daily_positive_sentiment, color="green", marker="^", label="Positive"
    )

    plt.title(f"{title} Sentiment vs {title} Price", fontsize=14)
    plt.xlabel("Date", fontsize=14)
    plt.ylabel("Weighted Sentiment Mean", fontsize=14)
    plt.legend()
    plt.grid(True)
    plt.show()


def graph(title):
    data_series = get_data_series()
    plot(title, *data_series)


if __name__ == "__main__":
    graph("Default")
