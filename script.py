import streamlit as st
import feedparser
import ssl
import re
from datetime import datetime
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
    
def replace_tag_with_boundary(match, text): 
    before = text[:match.start()] 
    if re.search(r'[.!?]"?\s*$', before): 
        return ' '
    else:
        return '. '


    

def get_relevant_articles(articles: list, keywords: list):
    relevant_articles = {}
    count = 1

    keyword_patterns = {
        keyword: re.compile(rf'\b{re.escape(keyword)}\b', re.IGNORECASE)
        for keyword in keywords
    }

    for article in articles:
        matched_keywords = set()
        matched_context = set()
       
        for key, value in article.items():
            if isinstance(value, str): 
                for keyword, pattern in keyword_patterns.items():
                    if pattern.search(value): 
                        matched_keywords.add(keyword)

                        text = value
                        text = re.sub(      
                            r'(</p>|<br\s*/?>|</div>)',
                            lambda m: replace_tag_with_boundary(m, text),
                            text,
                            flags=re.IGNORECASE
                        )
                        cleaned_value = re.sub(r'<[^>]+>', ' ', text)
                        cleaned_value = re.sub(r'\s+', ' ', cleaned_value).strip()

                        sentences = re.split(r'(?<=[.!?]")(?=\s+)|(?<=[.!?])(?=\s+)', cleaned_value)                        
                        for sentence in sentences:
                            if pattern.search(sentence):
                                    if key!="title" and key!="link": 
                                        highlighted_sentence = pattern.sub(lambda m: f"**{m.group(0)}**", sentence)
                                        matched_context.add(highlighted_sentence.strip())
        if not matched_context: 
            matched_context.add("Keyword found only in article title and/or URL.") 

        if matched_keywords: 
            relevant_articles[count] = {
                'Article Title': article.get('title'),
                'Article Link': article.get('link'),
                'Date and Time Published': article.get('published'),
                'Matched Keywords': matched_keywords,
                'Context': matched_context 
            }
            count += 1

    return relevant_articles




st.set_page_config(page_title="Incident Feed", layout="wide") 

st.title("Lab & Environmental Emergency News Monitor") 

with st.sidebar: 
    st.header("User Inputs:") 
    
    rss_input = st.text_area("RSS Feed URLs (one per line)",  
        value="""https://feeds.nbcnews.com/nbcnews/public/news
https://moxie.foxnews.com/google-publisher/health.xml
http://rss.cnn.com/rss/cnn_health.rss
https://www.wthr.com/feeds/syndication/rss/news/local
https://ktla.com/news/california/feed/
https://abc13.com/feed/""")
    
    keyword_input = st.text_input("Desired Keywords (comma-separated)", 
                                    value="asbestos, mold, explosion, chemical leak, gas leak, toxic leak, chemical explosion, flammable, chemical spill, toxic release, hazardous material, environmental accident, industrial fire, wildfire, refinery explosion, asbestos release, mold outbreak, mold remediation, asbestos abatement monitoring, superfund site incident, CERCLA site release, TSCA incident, NTSIP release incident, EPA envirofacts alert, chemical incident") 

    run_search = st.button("Run News Scan") 

if run_search: 
    rss_feeds = [url.strip() for url in rss_input.strip().splitlines() if url.strip()] 
    keywords = [kw.strip().lower() for kw in keyword_input.split(",") if kw.strip()] 
    
    with st.spinner("Scanning feeds for relevant articles..."): 
        articles = extract_articles(rss_feeds) 
        filtered_articles = get_relevant_articles(articles, keywords)

    st.subheader(f"Found {len(filtered_articles)} article(s) relevant to your desired keywords.") 

    for counter, article in filtered_articles.items(): 
        # st.markdown(f"### {counter}. {article['Article Title']}") #article title is bolded
        st.markdown(f"<h3 style='color:red;'>{counter}. {article['Article Title']}</h3>", unsafe_allow_html=True) #make article title red
        st.markdown(f"**Published:** {article['Date and Time Published']}")
        st.markdown(f"[Read Article]({article['Article Link']})") 
        st.markdown(f"**Matched Keyword(s):** {', '.join(kw.capitalize() for kw in article['Matched Keywords'])}")
        st.markdown(f"**Keyword Context:**\n\n-" + '\n\n-'.join(article['Context']))
        st.markdown("---")