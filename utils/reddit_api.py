import praw
import ssl
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

reddit = praw.Reddit(
    client_id="8etZ3kOpmdiNLX4KcTeeyA",
    client_secret="hSKd1-EVEe90CjagR3RLByBt8NkFxQ",
    user_agent="sentiment_analysis_app/1.0 by YourUsername"
)

url = "https://www.reddit.com/r/funny/comments/3g1jfi/buttons/"

submission = reddit.submission(url=url)
submission.comments.replace_more(limit=None)

for top_level_comment in submission.comments:
    print(top_level_comment.body)