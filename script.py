import streamlit as st
import feedparser
import ssl
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


def extract_articles(websites: list):
    articles = [] 
    for website in websites:
        feed = feedparser.parse(website) 
        for entry in feed.entries:
            article_data = {} 

            for key in ("title", "summary", "link", "published"): 
                if key in entry:
                    article_data[key] = entry[key]

            if "content" in entry and isinstance(entry["content"], list): 
                content_item = entry["content"][0]
                if "value" in content_item:
                    article_data["content"] = content_item["value"]

            articles.append(article_data)
    return articles
    

def get_relevant_articles(articles: list, keywords: list):   
    relevant_articles = {}
    count = 1
    for article in articles:
        for key, value in article.items(): 
            if isinstance(value, str) and any(keyword.lower() in value.lower() for keyword in keywords):
                title = article.get('title')
                link = article.get('link')
                published = article.get('published')
                relevant_articles[count] = {'Article Title': title, 'Article Link': link, 'Date and Time Published': published}
                count +=1
                break   
    return relevant_articles





st.set_page_config(page_title="Incident Feed", layout="wide") 

st.title("Lab & Environmental Emergency News Monitor") 

with st.sidebar: 
    st.header("User Inputs:") 
    
    rss_input = st.text_area("RSS Feed URLs (one per line)",  
        value="""https://feeds.nbcnews.com/nbcnews/public/news
http://rss.cnn.com/rss/cnn_us.rss""")
    
    keyword_input = st.text_input("Desired Keywords (comma-separated)", value="lab, fire, explosion, chemical, environmental") 

    run_search = st.button("Run News Scan") 

if run_search: 
    rss_feeds = [url.strip() for url in rss_input.strip().splitlines() if url.strip()] 
    keywords = [kw.strip().lower() for kw in keyword_input.split(",") if kw.strip()] 
    
    with st.spinner("Scanning feeds for relevant articles..."): 
        articles = extract_articles(rss_feeds) 
        filtered_articles = get_relevant_articles(articles, keywords)

    st.subheader(f"Found {len(filtered_articles)} articles relevant to your desired keywords!") 

    for counter, article in filtered_articles.items(): 
        st.markdown(f"### {counter}. {article['Article Title']}") 
        st.markdown(f"**Published:** {article['Date and Time Published']}")
        st.markdown(f"[Read Article]({article['Article Link']})") 
        st.markdown("---")