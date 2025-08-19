import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from utils.articles import display_articles, convert_articles_to_central, extract_articles, get_relevant_articles, remove_exact_duplicates


count = st_autorefresh(interval=400000, limit=None, key="autorefresh")

st.set_page_config(page_title="Incident Feed", layout="wide") 
st.image("Eurofins.png", width=500)
st.markdown(f"<p style='font-size:48px; font-weight:bold; color:#003883;'>Environmental Emergency News Monitor</p>", unsafe_allow_html=True)

with st.sidebar: 
    sort_options = [
    "None",
    "Published Date (Newest First)",
    "Number of Keywords Matched (Most)"]
    selected_sort = st.sidebar.selectbox("Sort articles by", sort_options)
    st.header("User Inputs:") 



    st.subheader("RSS Feeds (toggle defaults, or add new ones below)")
                    #detroit, cleveland, port arthur, san francisco, chicago, pittsburgh, denver, jersey city, sacramento
    default_rss = [  #national, new orleans, indianapolis, los angeles, hawaii, houston, philadelphia, baltimore, dallas
        "https://feeds.nbcnews.com/nbcnews/public/news",
"https://moxie.foxnews.com/google-publisher/us.xml",
"https://www.wthr.com/feeds/syndication/rss/news/local",
"https://ktla.com/news/california/feed/",
"https://abc13.com/feed/",
"https://www.latimes.com/nation/rss2.0.xml",
"https://www.staradvertiser.com/feed/",
"https://www.wdsu.com/topstories-rss",
"https://6abc.com/feed/",
"https://www.nbcchicago.com/?rss=y",
"https://www.wtae.com/topstories-rss",
"https://www.wxyz.com/news.rss",
"https://www.wkyc.com/feeds/syndication/rss/news",
"https://www.12newsnow.com/feeds/syndication/rss/news/local",
"https://abc7news.com/feed/",
"https://www.denver7.com/news/local-news.rss?_ga=2.23544893.620645875.1755100212-144600510.1755100212",
"https://hudsonreporter.com/news/jersey-city/feed/",
"https://www.pressherald.com/news/feed/",
"https://www.wmar2news.com/news/local-news.rss",
"https://www.wfaa.com/feeds/syndication/rss/news/local",
"https://www.kcra.com/topstories-rss"
                ]
    
    extra_rss_input = st.text_area("Extra RSS Feed URLs (one per line)", value="")
    extra_rss = [url.strip() for url in extra_rss_input.splitlines() if url.strip()]
    all_rss = default_rss + extra_rss
    selected_rss = []
    for feed in all_rss:
        if st.checkbox(feed, value=True, key=f"rss_{feed}"):
            selected_rss.append(feed)
    
    

    st.subheader("Keywords (toggle defaults, or add new ones below)")
    default_keywords = ["environmental cleanup",
"emergency environmental response",
"environmental remediation",
"pesticides",
"heavy metals",
"oil spill",
"herbicides",
"chromium",
"particulate",
"solvents",
"chemical materials",
"ammonia",
"chlorine",
"cyanide",
"arsenic",
"phenol",
"formaldehyde",
"hydrocarbons",
"VOC",
"volatile organic compounds",
"polychlorinated biphenyls",
"dioxins",
"benzene",
"toluene",
"Xylene",
"Nitric Acid",
"Sulfuric Acid",
"Hydrochloric Acid",
"Alkalis",
"Sodium Hydroxide",
"Potassium Hydroxide",
"Hydrogen Sulfide",
"Perchlorates",
"PFOA",
"PFOS",
"Hazardous waste",
"Industrial accident",
"Plant explosion",
"Factory fire",
"Pipeline leak",
"Tanker spill",
"Contaminated water",
"Groundwater contamination",
"Soil contamination",
"Air pollution",
"Smoke plume",
"Dust emission",
"Petroleum & Marine",
"Diesel spill",
"Fuel leak",
"Crude oil spill",
"Marine pollution",
"Offshore rig accident",
"Radioactive leak",
"Radiation exposure",
"Biohazard",
"Toxic release",
"Odor complaint",
"Fume release",
"toxic chemicals",
"asbestos",
"mold",
"explosion",
"explosions",
"chemical leak",
"gas leak",
"toxic leak",
"chemical explosion",
"flammable",
"chemical spill",
"toxic release",
"hazardous chemicals",
"hazardous material",
"hazardous materials",
"environmental accident",
"industrial fire",
"pasture fire",
"pipeline release",
"train derailment",
"PFAS",
"forever chemicals",
"refinery explosion",
"asbestos release",
"mold outbreak",
"mold remediation",
"asbestos abatement monitoring",
"superfund site incident",
"CERCLA site release",
"TSCA incident",
"NTSIP release incident",
"EPA envirofacts alert",
"chemical incident"]
    extra_keyword_input = st.text_area("Extra Keywords (one per line)", value="")
    extra_keywords = [kw.strip().lower() for kw in extra_keyword_input.splitlines() if kw.strip()]
    all_keywords = default_keywords + extra_keywords
    selected_keywords = []
    for kw in all_keywords:
        if st.checkbox(kw, value=True, key=f"kw_{kw}"):
            selected_keywords.append(kw)

    

    rss_feeds = selected_rss
    keywords = selected_keywords



  


with st.spinner("Scanning feeds for relevant articles..."): 
    articles = extract_articles(rss_feeds) 
    filtered_articles = get_relevant_articles(articles, keywords)


last_updated = datetime.now().strftime("%B %d, %Y at %I:%M:%S %p")
st.markdown(f"<p style='font-size:24px; font-weight:bold; color:#003883;'>Feed last updated: {last_updated}</p>",
    unsafe_allow_html=True)

filtered_articles = remove_exact_duplicates(filtered_articles)

st.subheader(f"Found {len(filtered_articles)} article(s) relevant to your desired keywords.") 

filtered_articles = convert_articles_to_central(filtered_articles)

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

display_articles(filtered_articles)


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