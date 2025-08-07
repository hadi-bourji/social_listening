import streamlit as st
import feedparser
#force Python to skip SSL certificate verification for HTTPS connections
import ssl
import re
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
    count = 1

    keyword_patterns = {
        keyword: re.compile(rf'\b{re.escape(keyword)}\b', re.IGNORECASE) #make a dict consisting of the original keyword as key and the processed keyword as value. Done to ensure we find exactly the word and not just if they keyword is a substring in the article
        for keyword in keywords
    }

    for article in articles:
        matched_keywords = set() #unique list

        for key, value in article.items():
            if isinstance(value, str): # make sure the article info is a string first
                for keyword, pattern in keyword_patterns.items():
                    if pattern.search(value): #if the processed keyword is in the article, add the original keyword to a set that contains all keywords in this article
                        matched_keywords.add(keyword)

        if matched_keywords: #if matched keywords contains a keyword that was matched we add all the info about this article to our relevant articles dict
            relevant_articles[count] = {
                'Article Title': article.get('title'),
                'Article Link': article.get('link'),
                'Date and Time Published': article.get('published'),
                'Matched Keywords': sorted(matched_keywords) 
            }
            count += 1

    return relevant_articles


st.set_page_config(page_title="Incident Feed", layout="wide") #set title that is shown in browser tab

st.title("Lab & Environmental Emergency News Monitor") #set title shown at top of webpage

with st.sidebar: #sidebar
    st.header("User Inputs:") #header for the sidebar
    
    rss_input = st.text_area("RSS Feed URLs (one per line)",  #creates a field for the web feed url inputs with a couple links put in by default for the user 
        value="""https://feeds.nbcnews.com/nbcnews/public/news
http://rss.cnn.com/rss/cnn_us.rss""")
    
    keyword_input = st.text_input("Desired Keywords (comma-separated)", value="lab, fire, explosion, chemical, environmental") #creates a field for the user to input keywords, with a list of default words

    run_search = st.button("Run News Scan") #creates a button with text telling the user what the button does

if run_search: #if the user clicks the button
    rss_feeds = [url.strip() for url in rss_input.strip().splitlines() if url.strip()] #we want to take all the text in the rss_feeds input box, and process them into a list of URLs
    keywords = [kw.strip().lower() for kw in keyword_input.split(",") if kw.strip()] #take all the text in keyword_input input box, split them by comma, if keyword.strip is not empty, append the lowercased keyword
    
    with st.spinner("Scanning feeds for relevant articles..."): # when user hits run button give this loading text
        articles = extract_articles(rss_feeds) #then run the two functions to get the relevant articles
        filtered_articles = get_relevant_articles(articles, keywords)

    st.subheader(f"Found {len(filtered_articles)} relevant articles!") #once the above has run, we output the text with the number of articles found

    for counter, article in filtered_articles.items(): #loop through the filtered_articles dictionary from our function
        st.markdown(f"### {counter}. {article['Article Title']}") #output the counter number (key) and the portion of the value that contains each info we want
        st.markdown(f"**Published:** {article['Date and Time Published']}")
        st.markdown(f"[Read Article]({article['Article Link']})") #create a hyperlink, user sees the text inside [] and text in () is the link
        st.markdown(f"Matched Keyword(s): {', '.join(article['Matched Keywords'])}")#add in the keyword that was matched for each article
        st.markdown("---") #divider