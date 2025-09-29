import praw
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

reddit = praw.Reddit(
    client_id="8etZ3kOpmdiNLX4KcTeeyA",
    client_secret="hSKd1-EVEe90CjagR3RLByBt8NkFxQ",
    user_agent="sentiment_analysis_app/1.0 by YourUsername"
)

for submission in reddit.subreddit("all").search("eurofins", limit=50):
    submission_date = datetime.fromtimestamp(submission.created_utc)
    print("Post title:", submission.title)
    print("URL:", submission.url)

    submission.comments.replace_more(limit=None)
    
    for top_level_comment in submission.comments:
        comment_date = datetime.fromtimestamp(top_level_comment.created_utc)
        score = analyzer.polarity_scores(top_level_comment.body)
        print("{} {:<65} {}".format(comment_date, top_level_comment.body, str(score["compound"])))

    
    print("---- End of Submission ----\n")