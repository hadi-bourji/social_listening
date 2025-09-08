import streamlit as st
import pandas as pd
import random
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from utils.articles import display_articles, update_feed_and_archive
from utils.archive import ensure_articles_table, save_articles_to_db, query_articles

random_approx_hour = random.uniform(3240000,3960000) #generate random number between .9 and 1.1 hours (converted to milliseconds) for autorefresh interval
ensure_articles_table() 
st_autorefresh(interval=random_approx_hour, limit=None, key="hourly_refresh")

# --- Page setup ---
st.set_page_config(page_title="Incident Feed", layout="wide")
st.image("Eurofins.png", width=500)
st.markdown(
    "<p style='font-size:48px; font-weight:bold; color:#003883;'>Environmental Emergency News Monitor</p>",
    unsafe_allow_html=True
)

ai_mode = st.checkbox("AI Mode", value=True,key="AI_mode")
st.info("AI mode applies a machine learning filter to help improve article relevance.")

# --- Sidebar exclusions ---
EXCLUDED_RSS_FILE = "excluded_rss.txt"
EXCLUDED_KEYWORDS_FILE = "excluded_keywords.txt"

def load_exclusions(filepath):
    """Load exclusions from a file (creates file if missing)."""
    if not os.path.exists(filepath):
        with open(filepath, "w"): 
            pass
    with open(filepath, "r") as f:
        return {line.strip() for line in f if line.strip()}

def add_to_exclusions(filepath, item):
    """Append an item to the exclusions file."""
    with open(filepath, "a") as f:
        f.write(item + "\n")

excluded_rss = load_exclusions(EXCLUDED_RSS_FILE)
excluded_keywords = load_exclusions(EXCLUDED_KEYWORDS_FILE)


# --- Sidebar Inputs ---
with st.sidebar:

    st.header("Search Current RSS Feeds", divider="blue")   
    # Sort options
    sort_options = ["None", "Published Date (Newest First)", "Number of Keywords Matched (Most)"]
    selected_sort = st.selectbox("Sort articles by", sort_options, key="sort_articles")
                     #wichita-kansas, st louis, 
                     #detroit, cleveland, port arthur, san francisco, chicago, pittsburgh, denver, jersey city, sacramento, seattle, st louis, brooklyn, boston
    default_rss = [  #national, new orleans, indianapolis, los angeles, hawaii, houston, philadelphia, baltimore, dallas, richmond virginia, raleigh, miami, tristate area
        "https://feeds.nbcnews.com/nbcnews/public/news",
        "https://moxie.foxnews.com/google-publisher/us.xml",
        "https://www.wthr.com/feeds/syndication/rss/news/local",
        "https://ktla.com/news/california/feed/",
        "https://abc13.com/feed/",
        "https://www.staradvertiser.com/feed/",
        "https://www.wdsu.com/topstories-rss",
        "https://6abc.com/feed/",
        "https://abc7chicago.com/feed/",
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
        "https://www.stltoday.com/search/?c=news%2Flocal*&d1=&d2=&s=start_time&sd=desc&l=50&f=rss&t=article,html,collection,link,video",
        "https://www.9news.com/feeds/syndication/rss/news/local",
        "https://brooklyneagle.com/feed/",
        "https://www.local10.com/arc/outboundfeeds/rss/category/news/local/?outputType=xml",
        "https://www.wcvb.com/topstories-rss",
        "https://www.ksn.com/news/local/feed/",
        "https://fox2now.com/news/feed/",
        "https://www.wbbjtv.com/feed/",
        "https://www.tristatehomepage.com/feed/"
    ]
    default_rss = [rss for rss in default_rss if rss not in excluded_rss]
    extra_rss_input = st.text_area("Extra RSS Feed URLs (one per line)", value="", key="extra_rss_input")
    extra_rss = [url.strip() for url in extra_rss_input.splitlines() if url.strip()]
    all_rss = default_rss + extra_rss
    select_all_rss = st.checkbox("Select/Deselect All Feeds", value=True, key="select_all_rss")
    selected_rss = [feed for feed in all_rss if st.checkbox(feed, value=select_all_rss, key=f"rss_{feed}")]

    #remove feed sites and add them to exclusion file
    st.markdown("---")
    rss_to_remove = st.selectbox("Delete a feed permanently", ["None"] + default_rss, key="remove_rss")
    if rss_to_remove != "None" and st.button("Delete Feed"):
        add_to_exclusions(EXCLUDED_RSS_FILE, rss_to_remove)
        st.success(f"Removed feed: {rss_to_remove}")
        st.rerun()
    st.markdown("---")
    # Keywords
    st.subheader("Keywords")
    # Match type
    match_type = st.radio("Keyword Match Type", ("Match any (OR)", "Match all (AND)"), index=0, key="match_type")
    default_keywords = [
        "Environmental Cleanup", "Emergency Environmental Response", "Environmental Remediation",
        "Pesticides", "Heavy Metals", "Oil Spill", "Herbicides", "Chromium", "Particulate",
        "Chemical Materials", "Ammonia", "Chlorine", "Cyanide", "Arsenic", "Phenol",
        "Formaldehyde", "Hydrocarbons", "VOC", "Toxic Gas", "Gas Exposure",
        "Volatile Organic Compounds", "Polychlorinated Biphenyls", "Dioxins", "Benzene",
        "Toluene", "Xylene", "Nitric Acid", "Sulfuric Acid", "Hydrochloric Acid", "Alkalis",
        "Sodium Hydroxide", "Potassium Hydroxide", "Hydrogen Sulfide", "Perchlorates",
        "PFOA", "PFOS", "Hazardous Waste", "Industrial Accident", "Plant Explosion",
        "Factory Fire", "Pipeline Leak", "Tanker Spill", "Contaminated Water",
        "Groundwater Contamination", "Soil Contamination", "Air Pollution", "Smoke Plume",
        "Dust Emission", "Diesel Spill", "Fuel Leak", "Marine Pollution",
        "Offshore Rig Accident", "Radioactive Leak", "Radiation Exposure", "Biohazard",
        "Toxic Release", "Odor Complaint", "Fume Release", "Toxic Chemicals", "Asbestos",
        "Mold", "Explosion", "Explosions", "Chemical Leak", "Gas Leak", "Toxic Leak",
        "Chemical Explosion", "Chemical Spill", "Hazardous Chemicals",
        "Hazardous Material", "Hazardous Materials", "Environmental Accident", "Industrial Fire",
        "Pipeline Release", "Train Derailment", "PFAS", "Forever Chemicals", "Refinery Explosion",
        "Asbestos Release", "Mold Outbreak", "Mold Remediation", "Asbestos Abatement Monitoring",
        "Chemical Incident", "Hazmat", "Environmental Hazards", "Environmental Hazard", "Chemical Fire"
    ]
    default_keywords = [kw for kw in default_keywords if kw not in excluded_keywords]
    extra_keyword_input = st.text_area("Extra Keywords (one per line)", value="", key="extra_keywords_input")
    extra_keywords = [kw.strip().lower() for kw in extra_keyword_input.splitlines() if kw.strip()]
    all_keywords = sorted(default_keywords + extra_keywords, key=lambda x: x.lower())
    select_all_keywords = st.checkbox("Select/Deselect All Keywords", value=True, key="select_all_keywords")
    selected_keywords = [kw for kw in all_keywords if st.checkbox(kw, value=select_all_keywords, key=f"kw_{kw}")]

    st.markdown("---")
    kw_to_remove = st.selectbox("Delete a keyword permanently", ["None"] + default_keywords, key="remove_kw")
    if kw_to_remove != "None" and st.button("Delete Keyword"):
        add_to_exclusions(EXCLUDED_KEYWORDS_FILE, kw_to_remove)
        st.success(f"Removed keyword: {kw_to_remove}")
        st.rerun()


# --- Tabs ---
tab_feed, tab_archive, tab_full_archive = st.tabs(["Live RSS Feed", "Archive Search", "Full Archive"])

# --- RSS Feed Search ---
with tab_feed:

    with st.spinner("Updating feeds and archiving..."):
        filtered_articles = update_feed_and_archive(selected_rss, selected_keywords, match_type, selected_sort, ai_mode)
     
    if st.button("Run RSS Feed Search", key="rss_search"):
        pass #when the user clicks the button it does a refresh of the entire script so it will run rss feed search by executing the search and archive function called above
        
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
with tab_archive:
    @st.fragment
    def search_archive():
        archive_match_type = st.radio(
            "Archive Keyword Match Type",
            ("Match any (OR)", "Match all (AND)"),
            index=0,
            key="archive_match_type"
        )
        keyword_filter = st.text_input("Keyword", key="archive_keyword")
        start_date = st.date_input("Start Date", key="archive_start_date")
        end_date = st.date_input("End Date", key="archive_end_date")
        # Search Current Archive 
        if st.button("Search Archive", key="archive_search"):
            with st.spinner("Scanning archives for relevant articles..."):
                archive_results = query_articles(
                    keywords=[kw.strip() for kw in keyword_filter.split(",") if kw.strip()],
                    start_date=start_date.strftime("%Y-%m-%d 00:00:00"),
                    end_date=end_date.strftime("%Y-%m-%d 23:59:59"),
                    archive_match_type="AND" if archive_match_type == "Match all (AND)" else "OR"
                )
                st.write(f"Found {len(archive_results)} articles")
                for article in archive_results:
                    st.markdown(f"**{article[1]}**")
                    st.markdown(f"[Read Article]({article[2]})")
                    st.markdown(f"Published: {article[3]}")
                    st.markdown(f"Context: {article[5]}")
                    st.markdown("---")
        # Archive Current Results
        if st.button("Archive Current News Feed Results", key="archive_save"):
            with st.spinner("Archiving current results..."):
                if filtered_articles:
                    new_count = save_articles_to_db(filtered_articles)
                    if new_count>0:
                        st.success(f"Archived {new_count} article(s) to the database!")
                    else:
                        st.success(f"No new articles archived.")
    search_archive()

#show full archive as a table
with tab_full_archive:
    st.subheader("Full Archive Table")
    # Fetch all articles from the database
    all_articles = query_articles()  # query_articles() with no args fetches everything
    if all_articles:
        # Convert to DataFrame for table display
        df = pd.DataFrame(all_articles, columns=["ID", "Article Title", "Web Link", "Published Date", "Keyword(s) Matched", "Context"])
        df["Published Date"] = pd.to_datetime(df["Published Date"], errors='coerce')
        # st.dataframe(df, use_container_width=True)
        st.data_editor(
    df,
    height=2000, 
    use_container_width=True,
    hide_index=True,
    column_config={
        "Web Link": st.column_config.LinkColumn("Web Link"),
        "Published Date": st.column_config.DatetimeColumn("Published Date", format="MMM DD, YYYY HH:mm:ss"),
        "Keyword(s) Matched": st.column_config.TextColumn("Keyword(s) Matched", width="medium"),
        "Context": st.column_config.TextColumn("Context", width=4500),
    }
)
    else:
        st.info("No archived articles found.")