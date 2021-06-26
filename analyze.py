import csv
import pickle
import urllib.request
from datetime import datetime, timedelta

from scipy.special import softmax
from torch.multiprocessing import Pool, cpu_count
from tqdm import tqdm
from transformers import AutoModelForSequenceClassification, AutoTokenizer


# Preprocess text (username and link placeholders)
def preprocess(text):
    new_text = []

    for t in text.split(" "):
        t = "@user" if t.startswith("@") and len(t) > 1 else t
        t = "http" if t.startswith("http") else t
        new_text.append(t)
    return " ".join(new_text)


def setup_model():
    MODEL = f"cardiffnlp/twitter-roberta-base-sentiment"

    tokenizer = AutoTokenizer.from_pretrained(MODEL)

    # download label mapping
    labels = []
    mapping_link = f"https://raw.githubusercontent.com/cardiffnlp/tweeteval/main/datasets/sentiment/mapping.txt"
    with urllib.request.urlopen(mapping_link) as f:
        html = f.read().decode("utf-8").split("\n")
        csvreader = csv.reader(html, delimiter="\t")
    labels = [row[1] for row in csvreader if len(row) > 1]

    # PT
    model = AutoModelForSequenceClassification.from_pretrained(MODEL)
    tokenizer.save_pretrained(MODEL)
    model.save_pretrained(MODEL)

    return model, tokenizer


def analyze_dict(date, model, tokenizer):
    with open(f"tweets_sentiment_{date}.csv", "w", encoding="utf-8") as f:
        write = csv.writer(f)
        fields = ["Text", "Retweets", "Negative", "Neutral", "Positive"]
        write.writerow(fields)

        tweet_dict = pickle.load(open(f"tweets_dict_{date}.pickle", "rb"))

        # FULL instance of Tweet
        # for tweet in tqdm(
        #     tweet_dict.values(),
        #     desc=f"Analyzing Tweets for {date}",
        #     total=len(tweet_dict),
        #     leave=False,
        # ):
        print(f"Beginning analysis for {date}...")
        for tweet in tweet_dict.values():
            text = preprocess(tweet.full_text)
            encoded_input = tokenizer(text, return_tensors="pt")
            output = model(**encoded_input)
            scores = output[0][0].detach().numpy()
            scores = softmax(scores)  # scores = [negative, neutral, positive]
            out_row = [tweet.full_text, tweet.retweet_count, *scores, tweet.id]
            write.writerow(out_row)

    print(f"Analysis for {date} complete.")


if __name__ == "__main__":
    # Out of curiosity, really.
    print("Number of processors: ", cpu_count())

    # Create the model and tokenizer to share amongst processes
    print("Setting up model...")
    model, tokenizer = setup_model()
    args = []
    # Package the args into tuples for each process
    for day in range(7, 0, -1):
        date = (datetime.today() - timedelta(days=day)).strftime("%Y-%m-%d")
        args += [(date, model, tokenizer)]
    print("Initiating analysis...")
    with Pool(7) as p:
        p.starmap(analyze_dict, args)

# ranking = np.argsort(scores)
# ranking = ranking[::-1]
# print(scores, ranking, labels)x
# for i in range(scores.shape[0]):
#     l = labels[ranking[i]]
#     s = scores[ranking[i]]
#     print(f"{i+1}) {l} {np.round(float(s), 4)}")
