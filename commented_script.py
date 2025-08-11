import streamlit as st #GUI
import feedparser #Parse through RSS
import re #processing text
#force Python to skip SSL certificate verification for HTTPS connections
import ssl
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

count = st_autorefresh(interval=10000, limit=None, key="autorefresh") #refresh every n milliseconds

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
function takes a tag and the text in the current field and returns either
a space if the text in the current field up to the current tag ends with punctuation
or a period if the text does not end with punctuation already
'''
def replace_tag_with_boundary(match, text): #match is the tag and text is the field
    before = text[:match.start()] #extract all text before the tag
    if re.search(r'[.!?]"?\s*$', before): #if this text before the tag ends with puntuation or punctuation followed by a quotation mark just return a space, otherwise return a period.
        return ' '
    else:
        return '. '
    

'''
function takes "articles" (list of dictionaries where each dictionary contains the relevant information for one article) and "keywords" (list of keywords we want to find articles about) as input
if article contains a keyword, clean up the field that the keyword was found in and split the field so we can identify only the sentence the keyword was found in
outputs "relevant_articles" list of articles that contain at least one of the provided keywords
'''

def get_relevant_articles(articles: list, keywords: list):
    relevant_articles = {}
    count = 1

    keyword_patterns = {
        keyword: re.compile(rf'\b{re.escape(keyword)}\b', re.IGNORECASE) #\b{keyword}\b means it matches the keyword as a whole word only so no false positives on substrings
        for keyword in keywords
    }

    for article in articles:
        matched_keywords = set() #use set since its a unique list-no duplicates 
        matched_context = set()
       
        for key, value in article.items():
            if isinstance(value, str): # make sure the article info is a string first
                for keyword, pattern in keyword_patterns.items(): #loop through keywords
                    if pattern.search(value): #if the processed keyword is in the article, add the original keyword to a set that contains all keywords in this article
                        matched_keywords.add(keyword) 

                        text = value
                        text = re.sub(      #along with replace_tag_with_boundary function above, this only replaces the tag with a period if there is no punctuation there already
                            r'(</p>|<br\s*/?>|</div>)',
                            lambda m: replace_tag_with_boundary(m, text),
                            text,
                            flags=re.IGNORECASE
                        )                        
                        cleaned_value = re.sub(r'<[^>]+>', ' ', text) #remove all other html tags
                        cleaned_value = re.sub(r'\s+', ' ', cleaned_value).strip() #clean up by replacing all spacing with a single space


                        sentences = re.split(r'(?<=[.!?]")(?=\s+)|(?<=[.!?])(?=\s+)', cleaned_value) #splits if there is a punctuation or punctuation followed by a quotation mark 
                        for sentence in sentences: #loop through sentences and if the keyword is in a sentence, bold it unless the keyword is found in the link
                            if pattern.search(sentence):
                                if key!="title" and key!="link": #dont put the title or the link in keyword context since they are already present at the top
                                        highlighted_sentence = pattern.sub(lambda m: f"**{m.group(0)}**", sentence) #bold the keyword
                                        matched_context.add(highlighted_sentence.strip())
        if not matched_context: #since we're not adding the title or article link to the context, we want to let them know where the keyword was found
            matched_context.add("Keyword found only in article title and/or website link.") #if the keyword is only found in the title and/or article link

        if matched_keywords: #if matched keywords is not empty we add all the info about this article to our relevant articles dict
            relevant_articles[count] = {
                'Article Title': article.get('title'),
                'Article Link': article.get('link'),
                'Date and Time Published': article.get('published'),
                'Matched Keywords': matched_keywords,
                'Context': matched_context 
            }
            count += 1

    return relevant_articles


'''
GUI code below using streamlit.
'''
st.set_page_config(page_title="Incident Feed", layout="wide") #set title that is shown in browser tab

st.title("Lab & Environmental Emergency News Monitor") #set title shown at top of webpage

with st.sidebar: #sidebar
    st.header("User Inputs:") #header for the sidebar
    
    rss_input = st.text_area("RSS Feed URLs (one per line)",  #creates a field for the web feed url inputs with a couple links put in by default for the user 
        value="""https://feeds.nbcnews.com/nbcnews/public/news
http://rss.cnn.com/rss/cnn_us.rss""")
    
    keyword_input = st.text_input("Desired Keywords (comma-separated)", value="lab, fire, explosion, chemical, environmental") #creates a field for the user to input keywords, with a list of default words

#     run_search = st.button("Run News Scan") #creates a button with text telling the user what the button does

# if run_search: #if the user clicks the button
rss_feeds = [url.strip() for url in rss_input.strip().splitlines() if url.strip()] #we want to take all the text in the rss_feeds input box, and process them into a list of URLs
keywords = [kw.strip().lower() for kw in keyword_input.split(",") if kw.strip()] #take all the text in keyword_input input box, split them by comma, if keyword.strip is not empty, append the lowercased keyword

with st.spinner("Scanning feeds for relevant articles..."): # when user hits run button give this loading text
    articles = extract_articles(rss_feeds) #then run the two functions to get the relevant articles
    filtered_articles = get_relevant_articles(articles, keywords)


last_updated = datetime.now().strftime("%B %d, %Y at %I:%M:%S %p") #add in last updated time/date
st.markdown(f"<p style='font-size:24px; font-weight:bold; color:blue;'>Feed last updated: {last_updated}</p>",
    unsafe_allow_html=True) #write update time and date with larger font size, bolded, and blue to pop out


st.subheader(f"Found {len(filtered_articles)} relevant articles!") #once the above has run, we output the text with the number of articles found

for counter, article in filtered_articles.items(): #loop through the filtered_articles dictionary from our function
    st.markdown(f"### {counter}. {article['Article Title']}") #output the counter number (key) and the portion of the value that contains each info we want
    st.markdown(f"**Published:** {article['Date and Time Published']}")
    st.markdown(f"[Read Article]({article['Article Link']})") #create a hyperlink, user sees the text inside [] and text in () is the link
    st.markdown(f"**Matched Keyword(s):** {', '.join(kw.capitalize() for kw in article['Matched Keywords'])}") #add in the keyword that was matched for each article and capitalize each keyword
    st.markdown("---") #divider