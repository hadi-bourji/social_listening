import feedparser
import ssl
import re
from dateutil import parser, tz
from datetime import datetime
import pytz
import streamlit as st

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
def convert_article_to_central(article, tzinfos=tzinfos):
    """
    Convert an article's published date to Central Time and add readable fields.
    """
    central = pytz.timezone("America/Chicago")
    date_str = article.get('Date and Time Published')

    if date_str:
        dt_with_tz = parser.parse(date_str, tzinfos=tzinfos)
        dt_central = dt_with_tz.astimezone(pytz.UTC).astimezone(central)
        article['datetime_obj'] = dt_central
        article['readable_time'] = dt_central.strftime("%I:%M %p %Z %m-%d-%Y")
    else:
        article['datetime_obj'] = datetime.min
        article['readable_time'] = "Published Date not Provided in RSS Feed"
    
    return article

def convert_articles_to_central(articles_dict):
    """
    Apply central time conversion to all articles in a dictionary.
    """
    return {k: convert_article_to_central(v) for k, v in articles_dict.items()}


def display_articles(articles):
    c = 1
    for counter, article in articles.items(): 
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

