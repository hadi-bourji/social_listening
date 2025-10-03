import praw
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from transformers import pipeline

reddit = praw.Reddit(
    client_id="8etZ3kOpmdiNLX4KcTeeyA",
    client_secret="hSKd1-EVEe90CjagR3RLByBt8NkFxQ",
    user_agent="sentiment_analysis_app/1.0 by YourUsername"
)

def vader():
    #https://github.com/cjhutto/vaderSentiment?tab=readme-ov-file
    analyzer = SentimentIntensityAnalyzer()

    for submission in reddit.subreddit("all").search("eurofins", limit=50):
        
        submission.comments.replace_more(limit=None, threshold=1)

        if len(submission.comments) == 0:
            continue

        print("Post title:", submission.title)
        print("URL:", submission.url)
        
        for top_level_comment in submission.comments:
            comment_date = datetime.fromtimestamp(top_level_comment.created_utc)
            score = analyzer.polarity_scores(top_level_comment.body)
            print("{} {:<65} {}".format(comment_date, top_level_comment.body, str(score["compound"])))

        
        print("---- End of Submission ----\n")


def blob():
    #https://textblob.readthedocs.io/en/dev/quickstart.html#sentiment-analysis
    c=0
    for submission in reddit.subreddit("all").search('title:"eurofins"', limit=100):
        
        submission.comments.replace_more(limit=None, threshold=1)

        if len(submission.comments) == 0:
            continue

        date = datetime.fromtimestamp(submission.created_utc)

        print(f"{submission.title} — {date:%Y-%m-%d}")
        print("URL:", submission.url)
        c+=1
        print("Count:", c)
        
        for top_level_comment in submission.comments:
            comment_date = datetime.fromtimestamp(top_level_comment.created_utc)
            score = TextBlob(top_level_comment.body).sentiment
            print("{} {:<65} {}".format(comment_date, top_level_comment.body, score))

        
        print("---- End of Submission ----\n")

def hf():
    # analyzer = pipeline("sentiment-analysis")
    analyzer = pipeline(model = "cardiffnlp/twitter-roberta-base-sentiment-latest")

    for submission in reddit.subreddit("all").search("eurofins", limit=100):
        
        submission.comments.replace_more(limit=None, threshold=1)

        if len(submission.comments) == 0:
            continue

        print("Post title:", submission.title)
        print("URL:", submission.url)
        
        for top_level_comment in submission.comments:
            comment_date = datetime.fromtimestamp(top_level_comment.created_utc)
            score = analyzer(top_level_comment.body)
            print("{} {:<65} {}".format(comment_date, top_level_comment.body, score))

        
        print("---- End of Submission ----\n")


if __name__ == "__main__":
    # vader()
    blob()
    # hf()