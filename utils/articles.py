import re
import pytz
import streamlit as st
import html
import os
from dateutil import parser, tz
from datetime import datetime
from utils.run_concurrent import extract_articles
from utils.archive import save_articles_to_db
from model_training.inference import ML_filter

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

def replace_tag_with_boundary(match, text): 
    before = text[:match.start()] 
    if re.search(r'[.!?]"?\s*$', before): 
        return ' '
    else:
        return '. '
    
def get_relevant_articles(articles: list, keywords: list, match_type="OR"):
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
        
        if match_type == "AND":
            condition = set(kw.lower() for kw in keywords).issubset(
                {kw.lower() for kw in matched_keywords}
            )
        else: 
            condition = bool(matched_keywords)

        if condition:
            relevant_articles[count] = {
                'Article Title': article.get('title'),
                'Article Link': article.get('link'),
                'Date and Time Published': article.get('published'),
                'Matched Keywords': matched_keywords,
                'Context': matched_context
            }
            count += 1
    return relevant_articles


def remove_exact_duplicates_and_international(d):
    exclude_intnl = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia", "Australia", "Austria",
    "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia",
    "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia",
    "Cameroon", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Congo",
    "Costa Rica", "Cote d'Ivoire", "Croatia", "Cuba", "Cyprus", "Czech Republic",
    "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea",
    "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece",
    "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Vatican City", "Honduras", "Hungary", "Iceland", "India",
    "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati",
    "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg",
    "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico",
    "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal",
    "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea", "North Macedonia", "Norway", "Oman", "Pakistan",
    "Palau", "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Romania",
    "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino",
    "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia",
    "Solomon Islands", "Somalia", "South Africa", "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden",
    "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago",
    "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "Uruguay", "Uzbekistan", 
    "Vanuatu", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe", "europe", "nordic", "spanish", "england", "british", "london",
    "paris", "senior discount"]

    exclude_countries_norm = [c.lower() for c in exclude_intnl]

    seen = []
    seen_titles = set() 
    unique = {}
    new_key = 1

    for key, val in d.items():

        all_text = " ".join(
            html.unescape(v).lower().replace("–", "-")
            for v in val.values() if isinstance(v, str)
        )

        if any(re.search(rf'\b{re.escape(country)}\w*', all_text) for country in exclude_countries_norm):
            continue
        
        title = val.get("Article Title", "").strip().lower()
        if title in seen_titles:
            continue

        if val not in seen:
            seen_titles.add(title)
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

        context_list = [html.unescape(sentence) for sentence in article['Context']]
        context_list = list(dict.fromkeys(context_list))   
        if len(context_list) > 3:
            context_list = context_list[:3]
        st.markdown(f"**Keyword Context:**\n\n-" + '\n\n-'.join(context_list))

        st.markdown("---")
        c+=1

def apply_ML_filter(d):
    new_dict = {}
    new_key = 1

    for val in d.values():
        
        title = val.get("Article Title", "").strip().lower()
        content = val.get("Context", [])
        content = [c.strip().lower() for c in content]
        sentences = [title] + content
        
        predictions = ML_filter(sentences)

        if 1 in predictions:
            new_dict[new_key] = val
            new_key += 1
    return new_dict

def update_feed_and_archive(selected_rss, selected_keywords, match_type, selected_sort=None, ai_mode=True):
    articles = extract_articles(selected_rss)
    filtered_articles = get_relevant_articles(articles, selected_keywords,match_type="AND" if match_type == "Match all (AND)" else "OR")
    filtered_articles = remove_exact_duplicates_and_international(filtered_articles)
    filtered_articles = convert_articles_to_central(filtered_articles)
    if ai_mode:
        filtered_articles = apply_ML_filter(filtered_articles)
    if selected_sort == "Published Date (Newest First)":
                filtered_articles = dict(
                    sorted(
                        filtered_articles.items(),
                        key=lambda item: item[1].get('datetime_obj') or datetime.min,
                        reverse=True
                    )
                )
    elif selected_sort == "Number of Keywords Matched (Most)":
        filtered_articles = dict(
            sorted(
                filtered_articles.items(),
                key=lambda item: len(item[1].get('Matched Keywords', [])),
                reverse=True
            )
        )

    st.session_state['filtered_articles'] = filtered_articles
    
    # Archive results
    if filtered_articles:
        new_count = save_articles_to_db(filtered_articles)
        if new_count>0:
            st.success(f"Archived {new_count} article(s) to the database!")
        else:
            st.success(f"No new articles archived.")
    return filtered_articles

def parse_date(date_str):

    date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)

    formats = [
        "%B %d, %Y",   # September 12, 2024
        "%b %d, %Y",   # Sep 12, 2024
        "%B %Y",       # September 2024
        "%b %Y",       # Sep 2024
        "%m/%d/%Y",    # 09/12/2024
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    return None 