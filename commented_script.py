import streamlit as st #GUI
import feedparser #Parse through RSS
import re #processing text
#force Python to skip SSL certificate verification for HTTPS connections
import ssl
import pytz
import streamlit.components.v1 as components
import random
from dateutil import parser, tz
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


                        sentences = re.split( #split exception for commonly used abbreviations (still splits if end with .")
                                                r"(?<!Mr\.)(?<!Mrs\.)(?<!Ms\.)(?<!Dr\.)(?<!Prof\.)(?<!Rev\.)(?<!Sr\.)(?<!Jr\.)"
                                                r"(?<!Jan\.)(?<!Feb\.)(?<!Mar\.)(?<!Apr\.)(?<!Jun\.)(?<!Jul\.)(?<!Aug\.)"
                                                r"(?<!Sep\.)(?<!Sept\.)(?<!Oct\.)(?<!Nov\.)(?<!Dec\.)(?<!St\.)(?<!U\.S\.)"
                                                r"(?<!U\.K\.)(?<!vs\.)(?<!etc\.)(?<!i\.e\.)(?<!e\.g\.)(?<=[.!?]\")(?=\s+)|"
                                                r"(?<!Mr\.)(?<!Mrs\.)(?<!Ms\.)(?<!Dr\.)(?<!Prof\.)(?<!Rev\.)(?<!Sr\.)(?<!Jr\.)"
                                                r"(?<!Jan\.)(?<!Feb\.)(?<!Mar\.)(?<!Apr\.)(?<!Jun\.)(?<!Jul\.)(?<!Aug\.)"
                                                r"(?<!Sep\.)(?<!Sept\.)(?<!Oct\.)(?<!Nov\.)(?<!Dec\.)(?<!St\.)(?<!U\.S\.)"
                                                r"(?<!U\.K\.)(?<!vs\.)(?<!etc\.)(?<!i\.e\.)(?<!e\.g\.)(?<=[.!?])(?=\s+)",
                                                cleaned_value
                                            )                        

                        for sentence in sentences: #loop through split sentences and if the keyword is in a sentence, bold it unless the keyword is found in the link
                            matched_in_sentence = [kw for kw, pat in keyword_patterns.items() if pat.search(sentence)] #check all keywords in each sentence
                            if matched_in_sentence and key not in ("title", "link"): #dont put the title or the link in keyword context since they are already present at the top
                                highlighted_sentence = sentence
                                for kw in matched_in_sentence:
                                    highlighted_sentence = keyword_patterns[kw].sub(lambda m: f"**{m.group(0)}**", highlighted_sentence) #bold all the keywords present in the current sentence
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

#remove duplicate values and foreign countries from filtered articles dictionary
def remove_exact_duplicates(d):
    exclude_countries = ["france", "spain", "uk", "russia", "ukraine", "germany", "europe", "mexico", "nordic", "spanish", "england"]

    seen = []
    unique = {}
    new_key = 1

    for key, val in d.items():

        all_text = " ".join(
            str(v).lower() for v in val.values() if isinstance(v, str)
        )
        if any(country in all_text for country in exclude_countries):
            continue

        if val not in seen:
            seen.append(val)
            unique[new_key] = val
            new_key += 1

    return unique

'''
GUI code below using streamlit.
'''
st.set_page_config(page_title="Incident Feed", layout="wide") #set title that is shown in browser tab

st.image("Eurofins.png", width=500)
st.markdown(f"<p style='font-size:48px; font-weight:bold; color:#003883;'>Environmental Emergency News Monitor</p>",
    unsafe_allow_html=True) #set title shown at top of webpage

with st.sidebar: #sidebar
    sort_options = [ #list of sort options for user to choose from, none by default
    "None",
    "Published Date (Newest First)",
    "Number of Keywords Matched (Most)"
]
    selected_sort = st.sidebar.selectbox("Sort articles by", sort_options) #allow user to pick sorting from a dropdown menu

    st.header("User Inputs:") #header for the sidebar
    
    rss_input = st.text_area("RSS Feed URLs (one per line)",  #creates a field for the web feed url inputs with a couple links put in by default for the user 
        value="""https://feeds.nbcnews.com/nbcnews/public/news
http://rss.cnn.com/rss/cnn_us.rss""")
    
    keyword_input = st.text_area(
    "Desired Keywords (one per line)",
    value="""environmental cleanup
Emergency environmental response
Environmental remediation
asbestos
mold
explosion
chemical leak
gas leak
toxic leak
chemical explosion
flammable
chemical spill
toxic release
hazardous material
hazardous materials
environmental accident
industrial fire
pasture fire
pipeline release
train derailment
wildland fire
wildfire
wildfires
brush fire
refinery explosion
asbestos release
mold outbreak
mold remediation
asbestos abatement monitoring
superfund site incident
CERCLA site release
TSCA incident
NTSIP release incident
EPA envirofacts alert
chemical incident"""
)
#     run_search = st.button("Run News Scan") #creates a button with text telling the user what the button does

# if run_search: #if the user clicks the button
rss_feeds = [url.strip() for url in rss_input.strip().splitlines() if url.strip()] #we want to take all the text in the rss_feeds input box, and process them into a list of URLs
keywords = [kw.strip().lower() for kw in keyword_input.splitlines() if kw.strip()] #take all the text in keyword_input input box, split them by comma, if keyword.strip is not empty, append the lowercased keyword

with st.spinner("Scanning feeds for relevant articles..."): # when user hits run button give this loading text
    articles = extract_articles(rss_feeds) #then run the two functions to get the relevant articles
    filtered_articles = get_relevant_articles(articles, keywords)


last_updated = datetime.now().strftime("%B %d, %Y at %I:%M:%S %p") #add in last updated time/date
st.markdown(f"<p style='font-size:24px; font-weight:bold; color:#003883;'>Feed last updated: {last_updated}</p>",
    unsafe_allow_html=True) #write update time and date with larger font size, bolded, and blue to pop out

filtered_articles = remove_exact_duplicates(filtered_articles) #remove any duplicate values from dict

st.subheader(f"Found {len(filtered_articles)} relevant articles!") #once the above has run, we output the text with the number of articles found

central = pytz.timezone("America/Chicago") #timezone we want to switch to


tzinfos = {
    "EST": tz.gettz("America/New_York"),    # Eastern Standard Time (UTC-5)
    "EDT": tz.gettz("America/New_York"),    # Eastern Daylight Time (UTC-4)
    "CST": tz.gettz("America/Chicago"),     # Central Standard Time (UTC-6)
    "CDT": tz.gettz("America/Chicago"),     # Central Daylight Time (UTC-5)
    "PST": tz.gettz("America/Los_Angeles"), # Pacific Standard Time (UTC-8)
    "PDT": tz.gettz("America/Los_Angeles"), # Pacific Daylight Time (UTC-7)
    "GMT": tz.gettz("GMT"),                  # Greenwich Mean Time (UTC+0)
    "UTC": tz.gettz("UTC"),
}

for counter, article in filtered_articles.items(): #loop through the filtered_articles dictionary from our function
    date_str = article.get('Date and Time Published') #pull date and time of publishing for this article
    if date_str:
        dt_with_tz = parser.parse(date_str, tzinfos=tzinfos) #parse date and time with dictionary to avoid parser misunderstanding time zone abbreviations
        dt_utc = dt_with_tz.astimezone(pytz.UTC) 
        dt_central = dt_utc.astimezone(central) #convert all time zones to central
        formatted_time = dt_central.strftime(f"%I:%M %p %Z %m-%d-%Y") #covnvert to readable string
        article['datetime_obj'] = dt_central #save converted time for sorting
        article['readable_time'] = formatted_time #save converted and formatted time for outputting for human readability
    else:
        article['datetime_obj'] = datetime.min #if the rss doesnt have publish date
        article['readable_time'] = "Unknown"


if selected_sort == "Published Date (Newest First)": #if they choose to sort by newest first, sort the dict by date
    filtered_articles = dict(
        sorted(
            filtered_articles.items(),
            key=lambda item: item[1].get('datetime_obj') or datetime.min,
            reverse=True
        )
    )

if selected_sort == "Keywords (Most)":
    filtered_articles = dict(
        sorted(
            filtered_articles.items(),
            key=lambda item: len(item[1].get('Matched Keywords', [])),
            reverse=True
        )
    )


c = 1
for counter, article in filtered_articles.items():
    st.markdown(f"### {c}. {article['Article Title']}") #output the counter number (key) and the portion of the value that contains each info we want
    st.markdown(f"<h3 style='color:#EE7D11;'>{c}. {article['Article Title']}</h3>", unsafe_allow_html=True) #make article title eurofins color
    st.markdown(f"**Published:** {article['readable_time']}")
    st.markdown(f"[Read Article]({article['Article Link']})") #create a hyperlink, user sees the text inside [] and text in () is the link
    st.markdown(f"**Matched Keyword(s):** {', '.join(kw.capitalize() for kw in article['Matched Keywords'])}") #add in the keyword that was matched for each article and capitalize each keyword
    
    context_list = list(article['Context']) #only output the first three context sentences if there are more than three to make it less messy
    if len(context_list) > 3:
        context_list = context_list[:3]
    st.markdown(f"**Keyword Context:**\n\n-" + '\n\n-'.join(context_list))

    st.markdown("---") #divider
    c+=1