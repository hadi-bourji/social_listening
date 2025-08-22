import streamlit as st
from datetime import datetime
from utils.articles import display_articles, convert_articles_to_central, get_relevant_articles, remove_exact_duplicates_and_international
from utils.concurrent import extract_articles
from utils.archive import *

# --- Page setup ---
st.set_page_config(page_title="Incident Feed", layout="wide")
st.image("Eurofins.png", width=500)
st.markdown(
    "<p style='font-size:48px; font-weight:bold; color:#003883;'>Environmental Emergency News Monitor</p>",
    unsafe_allow_html=True
)

# --- Sidebar Inputs ---
with st.sidebar:

    # Sort options
    sort_options = ["None", "Published Date (Newest First)", "Number of Keywords Matched (Most)"]
    selected_sort = st.selectbox("Sort articles by", sort_options)

    # RSS Feeds
    st.subheader("RSS Feeds") #detroit, cleveland, port arthur, san francisco, chicago, pittsburgh, denver, jersey city, sacramento, seattle, st louis
    default_rss = [  #national, new orleans, indianapolis, los angeles, hawaii, houston, philadelphia, baltimore, dallas, richmond virginia, raleigh, 
        "https://feeds.nbcnews.com/nbcnews/public/news",
"https://moxie.foxnews.com/google-publisher/us.xml",
"https://www.wthr.com/feeds/syndication/rss/news/local",
"https://ktla.com/news/california/feed/",
"https://abc13.com/feed/",
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
"https://www.kcra.com/topstories-rss",
"https://www.wric.com/app-feed",
"https://www.wral.com/news/rss/142/",
"https://www.king5.com/feeds/syndication/rss/news/local",
"https://fox2now.com/news/feed/"
                ]
    extra_rss_input = st.text_area("Extra RSS Feed URLs (one per line)", value="")
    extra_rss = [url.strip() for url in extra_rss_input.splitlines() if url.strip()]
    all_rss = default_rss + extra_rss
    select_all_rss = st.checkbox("Select/Deselect All Feeds", value=True, key="select_all_rss")
    selected_rss = [feed for feed in all_rss if st.checkbox(feed, value=select_all_rss, key=f"rss_{feed}")]

    # Keywords
    st.subheader("Keywords")
    # Match type
    match_type = st.radio("Keyword Match Type", ("Match any (OR)", "Match all (AND)"), index=0)
    default_keywords = ["environmental cleanup",
"emergency environmental response",
"environmental remediation",
"pesticides",
"heavy metals",
"oil spill",
"herbicides",
"chromium",
"particulate",
"chemical materials",
"ammonia",
"chlorine",
"cyanide",
"arsenic",
"phenol",
"formaldehyde",
"hydrocarbons",
"VOC",
"toxic gas",
"gas exposure",
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
"Diesel spill",
"Fuel leak",
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
"pipeline release",
"train derailment",
"PFAS",
"forever chemicals",
"refinery explosion",
"asbestos release",
"mold outbreak",
"mold remediation",
"asbestos abatement monitoring",
"chemical incident"]    
    extra_keyword_input = st.text_area("Extra Keywords (one per line)", value="")
    extra_keywords = [kw.strip().lower() for kw in extra_keyword_input.splitlines() if kw.strip()]
    all_keywords = sorted(default_keywords + extra_keywords, key=lambda x: x.lower())
    select_all_keywords = st.checkbox("Select/Deselect All Keywords", value=True, key="select_all_keywords")
    selected_keywords = [kw for kw in all_keywords if st.checkbox(kw, value=select_all_keywords, key=f"kw_{kw}")]



# --- RSS Feed Search ---
if st.button("Run RSS Feed Search"):
    with st.spinner("Scanning feeds for relevant articles..."):
        articles = extract_articles(selected_rss)
        filtered_articles = get_relevant_articles(articles, selected_keywords, match_type="AND" if match_type == "Match all (AND)" else "OR")
        filtered_articles = remove_exact_duplicates_and_international(filtered_articles)
        filtered_articles = convert_articles_to_central(filtered_articles)

        # Sorting
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

        # Store in session_state so other buttons can access it
        st.session_state['filtered_articles'] = filtered_articles

# Load filtered_articles from session_state if it exists
filtered_articles = st.session_state.get('filtered_articles', None)

# Show last updated time if there are articles
if filtered_articles:
    last_updated = datetime.now().strftime("%B %d, %Y at %I:%M:%S %p")
    st.markdown(
        f"<p style='font-size:24px; font-weight:bold; color:#003883;'>Feed last updated: {last_updated}</p>",
        unsafe_allow_html=True
    )
    st.subheader(f"Found {len(filtered_articles)} article(s) relevant to your desired keywords.")
    display_articles(filtered_articles)

# --- Archive Search & Save ---
with st.sidebar:
    st.header("Archives")
    archive_match_type = st.radio("Archive Keyword Match Type", ("Match any (OR)", "Match all (AND)"), index=0)
    keyword_filter = st.text_input("Keyword")
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")

    # Archive Search
    if st.button("Search Archive"):
        with st.spinner("Scanning archives for relevant articles..."):
            archive_results = query_articles(
                keywords=[kw.strip() for kw in keyword_filter.split(",") if kw.strip()],
                start_date = start_date.strftime("%Y-%m-%d 00:00:00"),
                end_date = end_date.strftime("%Y-%m-%d 23:59:59"),
                archive_match_type="AND" if archive_match_type == "Match all (AND)" else "OR"
            )
            st.write(f"Found {len(archive_results)} articles")
            for article in archive_results:
                st.markdown(f"**{article[1]}**")
                st.markdown(f"[Read Article]({article[2]})")
                st.markdown(f"Published: {article[3]}")
                st.markdown(f"Keywords: {article[4]}")
                st.markdown(f"Context: {article[5]}")
                st.markdown("---")

    # Archive Current Results
    if st.button("Archive Current Results"):
        with st.spinner("Archiving current results..."):
            if filtered_articles:
                save_articles_to_db(filtered_articles)
                st.success(f"Archived {len(filtered_articles)} article(s) to the database!")
            else:
                st.warning("No articles to archive.")
