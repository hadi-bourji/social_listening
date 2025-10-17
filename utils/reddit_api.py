import praw
from datetime import datetime, timezone
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from transformers import pipeline

reddit = praw.Reddit(
    client_id="8etZ3kOpmdiNLX4KcTeeyA",
    client_secret="hSKd1-EVEe90CjagR3RLByBt8NkFxQ",
    user_agent="sentiment_analysis_app/1.0 by YourUsername"
)


def show_posts():

    comments = 0

    for submission in reddit.subreddit("all").search("PFAS", sort="top", time_filter="year", limit = 100):

        comments += submission.num_comments

        print("Post title:", submission.title)
        print(f"URL: https://reddit.com{submission.permalink}")
        print("Comments:", submission.num_comments)
        print(f"Date:{datetime.fromtimestamp(submission.created_utc, tz=timezone.utc).isoformat()}")

    print(f"Total Comments: {comments}")


def last_12_month():
    '''
    Returns a list of the last 12 months
    '''
    now = datetime.now(timezone.utc)
    keys = []
    year, month = now.year, now.month
    month-=1
    if month==0:
        month=12
        year-=1
        
    for _ in range(12):
        keys.append(f"{year:04d}-{month:02d}")
        month -= 1
        if month == 0:
            month = 12
            year -= 1

    return list(reversed(keys))

def monthly_comment_totals(query):

    month_keys = last_12_month()
    totals = {k: 0 for k in month_keys}

    for submission in reddit.subreddit("all").search(query, sort="comments", time_filter="year", limit=1000):

        if submission.num_comments == 0:
            break

        dt = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc)
        key = dt.strftime("%Y-%m")
        if key in totals:
            totals[key] += submission.num_comments  

    return totals


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

    for submission in reddit.subreddit("all").search("eurofins", limit=1000):
        
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
    # blob()
    # hf()
    months = monthly_comment_totals("PFAS")
    print(months)