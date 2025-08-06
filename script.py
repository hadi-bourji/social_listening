import feedparser
#below lines force Python to skip SSL certificate verification for HTTPS connections
import ssl
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


'''
function takes a website as input and looks at all useful key value pairs for all news stories on the given website
useful keys are:
'title', 'summary', 'content' as these are the most likely locations to find the key words related to accidents
'link' to output the direct access to the article that is found to be related to an accident
'published' to make sure the date of the article is current/output the date to the user
function outputs a list of dictionaries where each dictionary contains the relevant information for one article
'''
def extract_articles_from_rss(website: str):

    feed = feedparser.parse(website) #feed rss data in
    articles = [] #list with information of all articles

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
function takes "articles" (list of dictionaries where each dictionary contains the relevant information for one article)
'''
def pick(articles):    
    for key,value in articles[0].items():
        print(f"{key}: {value}")
pick(extract_articles_from_rss('https://feeds.nbcnews.com/nbcnews/public/news'))









#Use this code to see the all the articles
# website = 'https://feeds.nbcnews.com/nbcnews/public/news'
# def view_all(website: str):
#     article_dictionary = feedparser.parse(website) #load in rss news feed site and put all information in dict
#     for i in article_dictionary.entries:
#         print(i)
# view_all('https://feeds.nbcnews.com/nbcnews/public/news')