import feedparser
#below lines force Python to skip SSL certificate verification for HTTPS connections
import ssl
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


'''
function takes a list of websites as input and looks at all useful key value pairs for all news articles on all websites provided
useful keys are:
'title', 'summary', 'content' as these are the most likely locations to find the key words related to accidents
'link' to output the direct access to the article that is found to be related to an accident
'published' to make sure the date of the article is current/output the date to the user
function outputs "articles" (a list of dictionaries where each dictionary contains the relevant information for one article)
'''
def extract_articles(websites: list):
    articles = [] #list with information of all articles
    for website in websites:
        feed = feedparser.parse(website) #feed rss data in
        for entry in feed.entries:
            article_data = {} #dict for current article

            for key in ("title", "summary", "link", "published"): #loop through the important keys and add these key/value pairs to our current article dict
                if key in entry:
                    article_data[key] = entry[key]

            if "content" in entry and isinstance(entry["content"], list): #make sure content key/value info is available for this article and that its a list. also make sure content has "value" inside since thats where the content informaiton is in the content
                content_item = entry["content"][0]
                if "value" in content_item:
                    article_data["content"] = content_item["value"]

            articles.append(article_data)
    
    return articles
    

'''
function takes "articles" (list of dictionaries where each dictionary contains the relevant information for one article) and "keywords" (list of keywords we want to find articles about) as input
outputs "relevant_articles" list of articles that contain at least one of the provided keywords
'''
def get_relevant_articles(articles: list, keywords: list):   
    relevant_articles = {}

    for article in articles:
        for key, value in article.items(): #for each key value pair for each article, we confirm that the value is a string and then check if any of the keywords are in the value
            if isinstance(value, str) and any(keyword.lower() in value.lower() for keyword in keywords):#if it is we take the article title, link, and publish time and put it in the dict relevant_articles which is the output
                title = article.get('title')
                link =article.get('link')
                published = article.get('published')
                relevant_articles[title] = {'link': link, 'published': published}
                break
            
    return relevant_articles

get_relevant_articles(extract_articles(['https://feeds.nbcnews.com/nbcnews/public/news',"http://rss.cnn.com/rss/cnn_us.rss"]), ["fort", "fedex"])


## Use this code to see all of the articles
# def view_all(website: str):
#     article_dictionary = feedparser.parse(website) #load in rss news feed site and put all information in dict
#     for i in article_dictionary.entries:
#         print("\n--------------")
#         for key, value in i.items():
#             print(f"{key}: {value}")

# view_all('http://rss.cnn.com/rss/cnn_us.rss')
