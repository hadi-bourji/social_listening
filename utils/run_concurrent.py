import feedparser
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


def fetch_and_parse(url):
    """Fetch a single feed and parse its entries."""
    feed = feedparser.parse(url)
    entries_list = []
    for entry in feed.entries:
        article_data = {}
        for key in ("title", "summary", "link", "published"):
            if key in entry:
                article_data[key] = entry[key]
        if "content" in entry and isinstance(entry["content"], list):
            content_item = entry["content"][0]
            if "value" in content_item:
                article_data["content"] = content_item["value"]
        entries_list.append(article_data)
    return entries_list

def extract_articles(websites, max_workers=7):
    """Fetch articles from multiple websites concurrently using submit."""
    articles = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(fetch_and_parse, url): url for url in websites}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                feed_articles = future.result()
            except Exception as e:
                print(f"Error fetching {url}: {e}")
            else:
                articles.extend(feed_articles)
    return articles