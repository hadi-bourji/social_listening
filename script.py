import streamlit as st
import feedparser
import ssl
import re
import pytz
import streamlit.components.v1 as components
import random
from dateutil import parser, tz
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

count = st_autorefresh(interval=400000, limit=None, key="autorefresh")

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
                        sentences = re.split(
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
                       
                        for sentence in sentences:
                            matched_in_sentence = [kw for kw, pat in keyword_patterns.items() if pat.search(sentence)]
                            if matched_in_sentence and key not in ("title", "link"):
                                highlighted_sentence = sentence
                                for kw in matched_in_sentence:
                                    highlighted_sentence = keyword_patterns[kw].sub(lambda m: f"**{m.group(0)}**", highlighted_sentence)
                                matched_context.add(highlighted_sentence.strip())

        if not matched_context: 
            matched_context.add("Keyword found in article title and/or URL.") 

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


st.set_page_config(page_title="Incident Feed", layout="wide") 

st.image("Eurofins.png", width=500)

st.markdown(f"<p style='font-size:48px; font-weight:bold; color:#003883;'>Environmental Emergency News Monitor</p>",
    unsafe_allow_html=True)

with st.sidebar: 
    sort_options = [
    "None",
    "Published Date (Newest First)",
    "Number of Keywords Matched (Most)"
]

    selected_sort = st.sidebar.selectbox("Sort articles by", sort_options)
    
    st.header("User Inputs:") 
                                                              #detroit, cleveland, port arthur, san francisco, chicago, pittsburgh, denver, jersey city, sacramento
    rss_input = st.text_area("RSS Feed URLs (one per line)",  #national, new orleans, indianapolis, los angeles, hawaii, houston, philadelphia, baltimore, dallas
        value="""https://feeds.nbcnews.com/nbcnews/public/news
https://moxie.foxnews.com/google-publisher/us.xml
https://www.wthr.com/feeds/syndication/rss/news/local
https://ktla.com/news/california/feed/
https://abc13.com/feed/
https://www.latimes.com/nation/rss2.0.xml
https://www.staradvertiser.com/feed/
https://www.wdsu.com/topstories-rss
https://6abc.com/feed/
https://www.nbcchicago.com/?rss=y
https://www.wtae.com/topstories-rss
https://www.wxyz.com/news.rss
https://www.wkyc.com/feeds/syndication/rss/news
https://www.12newsnow.com/feeds/syndication/rss/news/local
https://abc7news.com/feed/
https://www.denver7.com/news/local-news.rss?_ga=2.23544893.620645875.1755100212-144600510.1755100212
https://hudsonreporter.com/news/jersey-city/feed/
https://www.pressherald.com/news/feed/
https://www.wmar2news.com/news/local-news.rss
https://www.wfaa.com/feeds/syndication/rss/news/local
https://www.kcra.com/topstories-rss
https://www.theguardian.com/us/environment/rss
                """)

    keyword_input = st.text_area(
    "Desired Keywords (one per line)",
    value="""environmental cleanup
emergency environmental response
environmental remediation
pesticides
heavy metals
oil spill
herbicides
chromium
particulate
solvents
chemical materials
ammonia
chlorine
cyanide
arsenic
phenol
formaldehyde
hydrocarbons
VOC
volatile organic compounds
polychlorinated biphenyls
dioxins
benzene
toluene
Xylene
Nitric Acid
Sulfuric Acid
Hydrochloric Acid
Alkalis
Sodium Hydroxide
Potassium Hydroxide
Hydrogen Sulfide
Perchlorates
PFOA 
PFOS 
Hazardous waste
Industrial accident
Plant explosion
Factory fire
Pipeline leak
Tanker spill
Contaminated water
Groundwater contamination
Soil contamination
Air pollution
Smoke plume
Dust emission
Petroleum & Marine
Diesel spill
Fuel leak
Crude oil spill
Marine pollution
Offshore rig accident
Radioactive leak
Radiation exposure
Biohazard
Toxic release
Odor complaint
Fume release
toxic chemicals
asbestos
mold
explosion
explosions
chemical leak
gas leak
toxic leak
chemical explosion
flammable
chemical spill
toxic release
hazardous chemicals
hazardous material
hazardous materials
environmental accident
industrial fire
pasture fire
pipeline release
train derailment
PFAS
forever chemicals
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



rss_feeds = [url.strip() for url in rss_input.strip().splitlines() if url.strip()] 
keywords = [kw.strip().lower() for kw in keyword_input.splitlines() if kw.strip()]


with st.spinner("Scanning feeds for relevant articles..."): 
    articles = extract_articles(rss_feeds) 
    filtered_articles = get_relevant_articles(articles, keywords)


last_updated = datetime.now().strftime("%B %d, %Y at %I:%M:%S %p")
st.markdown(f"<p style='font-size:24px; font-weight:bold; color:#003883;'>Feed last updated: {last_updated}</p>",
    unsafe_allow_html=True)


filtered_articles = remove_exact_duplicates(filtered_articles)

st.subheader(f"Found {len(filtered_articles)} article(s) relevant to your desired keywords.") 


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


central = pytz.timezone("America/Chicago")
for counter, article in filtered_articles.items(): 
    date_str = article.get('Date and Time Published')
    if date_str:
        dt_with_tz = parser.parse(date_str, tzinfos=tzinfos)
        dt_utc = dt_with_tz.astimezone(pytz.UTC)
        dt_central = dt_utc.astimezone(central)
        formatted_time = dt_central.strftime("%I:%M %p %Z %m-%d-%Y")
        article['datetime_obj'] = dt_central
        article['readable_time'] = formatted_time
    else:
        article['datetime_obj'] = datetime.min
        article['readable_time'] = "Published Date not Provided in RSS Feed"


if selected_sort == "Published Date (Newest First)":
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
    st.markdown(f"<h3 style='color:#EE7D11;'>{c}. {article['Article Title']}</h3>", unsafe_allow_html=True)
    st.markdown(f"**Published:** {article['readable_time']}")
    st.markdown(f"[Read Article]({article['Article Link']})") 
    st.markdown(f"**Matched Keyword(s):** {', '.join(kw.capitalize() for kw in article['Matched Keywords'])}")

    context_list = list(article['Context'])
    if len(context_list) > 3:
        context_list = context_list[:3]
    st.markdown(f"**Keyword Context:**\n\n-" + '\n\n-'.join(context_list))

    st.markdown("---")
    c+=1

#autoscroll code (instantly scrolls to bottom)
# html_code = f"""
# <div id="scroll-to-me" style='background: cyan; height=1px;'>hi</div>
# <script id="{random.randint(1000, 9999)}">
#    var e = document.getElementById("scroll-to-me");
#    if (e) {{
#      e.scrollIntoView({{behavior: "smooth"}});
#      e.remove();
#    }}
# </script>
# """
# components.html(html_code)
