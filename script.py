import streamlit as st
import pandas as pd
import random
import os
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz
from streamlit_autorefresh import st_autorefresh
from utils.articles import display_articles, update_feed_and_archive, parse_date
from utils.archive import ensure_articles_table, save_articles_to_db, query_articles, save_press_releases_to_db
from utils.web_scraper import pacelabs_scraper, epa_scraper, sgs_scraper, montrose_scraper, gel_scraper, emsl_scraper, babcock_scraper, wecklabs_scraper, alsglobal_scraper, microbac_scraper
from utils.reddit_api import last_12_month, monthly_comment_totals
from streamlit_tags import st_tags

random_approx_hour = random.uniform(3240000,3960000) #generate random number between .9 and 1.1 hours (converted to milliseconds) for autorefresh interval
ensure_articles_table() 
st_autorefresh(interval=random_approx_hour, limit=None, key="hourly_refresh")

# --- Page setup ---
st.set_page_config(page_title="Incident Feed", layout="wide")
st.image("Eurofins.png", width=500)
st.markdown(
    "<p style='font-size:48px; font-weight:bold; color:#003883;'>Environmental News Monitor</p>",
    unsafe_allow_html=True
)

# --- Sidebar exclusions ---
EXCLUDED_RSS_FILE = "excluded_rss.txt"
EXCLUDED_KEYWORDS_FILE = "excluded_keywords.txt"
USER_RSS_FILE = "user_rss.txt"
USER_KEYWORD_FILE = "user_keyword.txt"

def load_files(filepath):
    """Load user customizations from a file (creates file if missing)."""
    if not os.path.exists(filepath):
        with open(filepath, "w"): 
            pass
    with open(filepath, "r") as f:
        return {line.strip() for line in f if line.strip()}

def add_to_file(filepath, item):
    """Append an item to the file."""
    with open(filepath, "a") as f:
        f.write(item + "\n")

def remove_from_file(filepath, item):
    """Remove a line from a file."""
    if not os.path.exists(filepath):
        return
    with open(filepath, "r") as f:
        lines = f.readlines()
    with open(filepath, "w") as f:
        for line in lines:
            if line.strip() != item:
                f.write(line)


excluded_rss = load_files(EXCLUDED_RSS_FILE)
excluded_keywords = load_files(EXCLUDED_KEYWORDS_FILE)
user_rss = load_files(USER_RSS_FILE)
user_keyword = load_files(USER_KEYWORD_FILE)

if "user_keyword_set" not in st.session_state:
    st.session_state.user_keyword_set = user_keyword

if "user_rss_set" not in st.session_state:
    st.session_state.user_rss_set = user_rss

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
        "https://www.tristatehomepage.com/feed/",
        "https://envnewsbits.info/feed/"
    ]

    default_rss = [rss for rss in default_rss if rss not in excluded_rss]
    extra_rss_input = st.text_area("Extra RSS Feed URLs (one per line)", value="", key="extra_rss_input")

    if extra_rss_input.strip():
        new_feeds = [line.strip() for line in extra_rss_input.splitlines() if line.strip()]
        for feed in new_feeds:
            if feed in excluded_rss:
                excluded_rss.remove(feed)
                remove_from_file(EXCLUDED_RSS_FILE, feed)

            if feed not in user_rss:
                add_to_file(USER_RSS_FILE, feed)
                st.session_state.user_rss_set.add(feed)

    all_rss = default_rss + list(st.session_state.user_rss_set)

    

    with st.expander("Manage RSS Feeds"):
         
        select_all_rss = st.checkbox("Select/Deselect All Feeds", value=True, key="select_all_rss")
        selected_rss = [feed for feed in all_rss if st.checkbox(feed, value=select_all_rss, key=f"rss_{feed}")]


    # Keywords
    st.subheader("Keywords")
    # Match type
    match_type = st.radio("Keyword Match Type", ("Match any (OR)", "Match all (AND)"), index=0, key="match_type")
    default_keywords = [
        "Environmental Cleanup", "Emergency Environmental Response", "Environmental Remediation",
        "Pesticides", "Oil Spill", "Herbicides", "Chromium", "Particulate",
        "Chemical Materials", "Ammonia", "Chlorine", "Cyanide", "Arsenic", "Phenol",
        "Hydrocarbons", "VOC", "Toxic Gas", "Gas Exposure",
        "Volatile Organic Compounds", "Polychlorinated Biphenyls", "Dioxins", "Benzene",
        "Toluene", "Xylene", "Nitric Acid", "Sulfuric Acid", "Hydrochloric Acid", "Alkalis",
        "Sodium Hydroxide", "Potassium Hydroxide", "Hydrogen Sulfide", "Perchlorates",
        "PFOA", "PFOS", "Hazardous Waste", "Industrial Accident", "Plant Explosion",
        "Factory Fire", "Pipeline Leak", "Tanker Spill", "Contaminated Water",
        "Groundwater Contamination", "Soil Contamination", "Air Pollution", "Smoke Plume",
        "Dust Emission", "Diesel Spill", "Fuel Leak", "Marine Pollution",
        "Offshore Rig Accident", "Radioactive Leak", "Radiation Exposure", "Biohazard",
        "Toxic Release", "Odor Complaint", "Fume Release", "Toxic Chemicals", "Asbestos",
        "Explosion", "Explosions", "Chemical Leak", "Gas Leak", "Toxic Leak",
        "Chemical Explosion", "Chemical Spill", "Hazardous Chemicals",
        "Hazardous Material", "Hazardous Materials", "Environmental Accident", "Industrial Fire",
        "Pipeline Release", "Train Derailment", "PFAS", "Forever Chemicals", "Refinery Explosion",
        "Asbestos Release", "Mold Outbreak", "Mold Remediation", "Asbestos Abatement Monitoring",
        "Chemical Incident", "Hazmat", "Environmental Hazards", "Environmental Hazard", "Chemical Fire"
    ]
    default_keywords = [kw for kw in default_keywords if kw not in excluded_keywords]
    
    all_keywords = sorted(default_keywords + list(st.session_state.user_keyword_set), key=lambda x: x.lower())

    with st.expander("Manage Keywords"):
        
        selected_keywords = st_tags(label='', text='Add a keyword', value=all_keywords, suggestions= [], maxtags=-1, key='keyword_tag_input')
    
    for word in selected_keywords:
        if word not in all_keywords:
            if word in excluded_keywords:
                excluded_keywords.remove(word)
                remove_from_file(EXCLUDED_KEYWORDS_FILE, word)

            if word not in user_keyword:
                add_to_file(USER_KEYWORD_FILE, word)
                st.session_state.user_keyword_set.add(word)



# --- Tabs ---
tab_press_release, tab_feed, tab_archive, tab_full_archive, tab_keyword_trends, tab_settings = st.tabs([ "Industry & Regulatory Updates", "Live RSS Feed","Archive Search",
                                                                                                         "Full Archive", "Keyword Trends", "Settings"])

with tab_press_release:
    today = datetime.today().date()
    last_month = today - timedelta(days=30)
    st.markdown("### Filter by Date Range")
    start_date, end_date = st.date_input("Select date range:", value=[last_month, today])

    st.markdown(
    """
    <a href="https://www.epa.gov/newsreleases/search" target="_blank" 
       style="text-decoration:none; color:#003883;">
        <p style='font-size:48px; font-weight:bold; margin:0;'>
            United States Environmental Protection Agency (EPA)
        </p>
    </a>
    """,
    unsafe_allow_html=True)
    epa_articles = epa_scraper()
    c = 1
    for article in epa_articles:
        article_date = parse_date(article['date'])
        if article_date and start_date <= article_date <= end_date:
            st.markdown(f"<h3 style='color:#EE7D11;'>{c}. {article['title']}</h3>", unsafe_allow_html=True)
            st.markdown(f"**Published:** {article['date']}")
            st.markdown(f"[Read Article]({article['url']})") 
            st.markdown(f"**Description:** {article['description']}")

            st.markdown("---")
            c+=1
            save_press_releases_to_db([article])
    if c==1:
        st.markdown(f"<h3 style='color:#EE7D11;'>No press releases were published during the selected date range.", unsafe_allow_html=True)
        st.markdown("---")


    st.markdown(
    """
    <a href="https://www.pacelabs.com/company/press-releases-and-articles/" target="_blank" 
       style="text-decoration:none; color:#003883;">
        <p style='font-size:48px; font-weight:bold; margin:0;'>
            Pace Analytics Labs
        </p>
    </a>
    """,
    unsafe_allow_html=True)
    pacelabs_articles = pacelabs_scraper()
    c = 1
    for article in pacelabs_articles:
        article_date = parse_date(article['date'])
        if article_date and start_date <= article_date <= end_date:
            st.markdown(f"<h3 style='color:#EE7D11;'>{c}. {article['title']}</h3>", unsafe_allow_html=True)
            st.markdown(f"**Published:** {article['date']}")
            st.markdown(f"[Read Article]({article['url']})") 
            st.markdown(f"**Description:** {article['description']}")

            st.markdown("---")
            c+=1
            save_press_releases_to_db([article])
    if c==1:
        st.markdown(f"<h3 style='color:#EE7D11;'>No press releases were published during the selected date range.", unsafe_allow_html=True)
        st.markdown("---")


    st.markdown(
    """
    <a href="https://www.sgs.com/en/news" target="_blank" 
       style="text-decoration:none; color:#003883;">
        <p style='font-size:48px; font-weight:bold; margin:0;'>
            SGS (Société Générale de Surveillance) 
        </p>
    </a>
    """,
    unsafe_allow_html=True)       
    sgs_articles = sgs_scraper()
    c = 1
    for article in sgs_articles:
        article_date = parse_date(article['date'])
        if article_date and start_date <= article_date <= end_date:
            st.markdown(f"<h3 style='color:#EE7D11;'>{c}. {article['title']}</h3>", unsafe_allow_html=True)
            st.markdown(f"**Published:** {article['date']}")
            st.markdown(f"[Read Article]({article['url']})") 
            st.markdown(f"**Description:** {article['description']}")

            st.markdown("---")
            c+=1
            save_press_releases_to_db([article])
    if c==1:
        st.markdown(f"<h3 style='color:#EE7D11;'>No press releases were published during the selected date range.", unsafe_allow_html=True)
        st.markdown("---")


    st.markdown(
    """
    <a href="https://montrose-env.com/news-events/" target="_blank" 
       style="text-decoration:none; color:#003883;">
        <p style='font-size:48px; font-weight:bold; margin:0;'>
            Montrose Environmental
        </p>
    </a>
    """,
    unsafe_allow_html=True)    
    montrose_articles = montrose_scraper()
    c = 1
    for article in montrose_articles:
        article_date = parse_date(article['date'])
        if article_date and start_date <= article_date <= end_date:
            st.markdown(f"<h3 style='color:#EE7D11;'>{c}. {article['title']}</h3>", unsafe_allow_html=True)
            st.markdown(f"**Published:** {article['date']}")
            st.markdown(f"[Read Article]({article['url']})") 
            st.markdown(f"**Description:** {article['description']}")

            st.markdown("---")
            c+=1
            save_press_releases_to_db([article])
    if c==1:
        st.markdown(f"<h3 style='color:#EE7D11;'>No press releases were published during the selected date range.", unsafe_allow_html=True)
        st.markdown("---")


    st.markdown(
    """
    <a href="https://www.gel.com/blog" target="_blank" 
       style="text-decoration:none; color:#003883;">
        <p style='font-size:48px; font-weight:bold; margin:0;'>
            GEL Laboratories LLC
        </p>
    </a>
    """,
    unsafe_allow_html=True)    
    gel_articles = gel_scraper()
    c = 1
    for article in gel_articles:
        article_date = parse_date(article['date'])
        if article_date and start_date <= article_date <= end_date:
            st.markdown(f"<h3 style='color:#EE7D11;'>{c}. {article['title']}</h3>", unsafe_allow_html=True)
            st.markdown(f"**Published:** {article['date']}")
            st.markdown(f"[Read Article]({article['url']})") 
            st.markdown(f"**Description:** {article['description']}")

            st.markdown("---")
            c+=1
            save_press_releases_to_db([article])
    if c==1:
        st.markdown(f"<h3 style='color:#EE7D11;'>No press releases were published during the selected date range.", unsafe_allow_html=True)
        st.markdown("---")


    st.markdown(
    """
    <a href="https://emsl.com/News.aspx" target="_blank" 
       style="text-decoration:none; color:#003883;">
        <p style='font-size:48px; font-weight:bold; margin:0;'>
            EMSL Analytical
        </p>
    </a>
    """,
    unsafe_allow_html=True)    
    emsl_articles = emsl_scraper()
    c = 1
    for article in emsl_articles:
        article_date = parse_date(article['date'])
        if article_date and start_date <= article_date <= end_date:
            st.markdown(f"<h3 style='color:#EE7D11;'>{c}. {article['title']}</h3>", unsafe_allow_html=True)
            st.markdown(f"**Published:** {article['date']}")
            st.markdown(f"[Read Article]({article['url']})") 
            st.markdown(f"**Description:** {article['description']}")

            st.markdown("---")
            c+=1
            save_press_releases_to_db([article])
    if c==1:
        st.markdown(f"<h3 style='color:#EE7D11;'>No press releases were published during the selected date range.", unsafe_allow_html=True)
        st.markdown("---")


    # st.markdown(
    # """
    # <a href="https://www.babcocklabs.com/news" target="_blank" 
    #    style="text-decoration:none; color:#003883;">
    #     <p style='font-size:48px; font-weight:bold; margin:0;'>
    #         Babcock Laboratories
    #     </p>
    # </a>
    # """,
    # unsafe_allow_html=True)    
    # babcock_articles = babcock_scraper()
    # c = 1
    # for article in babcock_articles:
    #     article_date = parse_date(article['date'])
    #     if article_date and start_date <= article_date <= end_date:
    #         st.markdown(f"<h3 style='color:#EE7D11;'>{c}. {article['title']}</h3>", unsafe_allow_html=True)
    #         st.markdown(f"**Published:** {article_date.strftime('%B %d, %Y')}")
    #         st.markdown(f"[Read Article]({article['url']})") 
    #         st.markdown(f"**Description:** {article['description']}")

    #         st.markdown("---")
    #         c+=1
    #         save_press_releases_to_db([article])
    # if c==1:
    #     st.markdown(f"<h3 style='color:#EE7D11;'>No press releases were published during the selected date range.", unsafe_allow_html=True)
    #     st.markdown("---")


    st.markdown(
    """
    <a href="https://www.wecklabs.com/Company/SocialNetworking/News.aspx" target="_blank" 
       style="text-decoration:none; color:#003883;">
        <p style='font-size:48px; font-weight:bold; margin:0;'>
            Weck Laboratories
        </p>
    </a>
    """,
    unsafe_allow_html=True)    
    wecklabs_articles = wecklabs_scraper()
    c = 1
    for article in wecklabs_articles:
        article_date = parse_date(article['date'])
        if article_date and start_date <= article_date <= end_date:
            st.markdown(f"<h3 style='color:#EE7D11;'>{c}. {article['title']}</h3>", unsafe_allow_html=True)
            st.markdown(f"**Published:** {article['date']}")
            st.markdown(f"[Read Article]({article['url']})") 
            st.markdown(f"**Description:** {article['description']}")

            st.markdown("---")
            c+=1
            save_press_releases_to_db([article])
    if c==1:
        st.markdown(f"<h3 style='color:#EE7D11;'>No press releases were published during the selected date range.", unsafe_allow_html=True)
        st.markdown("---")
    

    st.markdown(
    """
    <a href="https://www.alsglobal.com/en/news-and-media" target="_blank" 
       style="text-decoration:none; color:#003883;">
        <p style='font-size:48px; font-weight:bold; margin:0;'>
            ALS (Australian Laboratory Services)
        </p>
    </a>
    """,
    unsafe_allow_html=True)    
    als_articles = alsglobal_scraper()
    c = 1
    for article in als_articles:
        article_date = parse_date(article['date'])
        if article_date and start_date <= article_date <= end_date:
            st.markdown(f"<h3 style='color:#EE7D11;'>{c}. {article['title']}</h3>", unsafe_allow_html=True)
            st.markdown(f"**Published:** {article['date']}")
            st.markdown(f"[Read Article]({article['url']})") 
            st.markdown(f"**Description:** {article['description']}")

            st.markdown("---")
            c+=1
            save_press_releases_to_db([article])
    if c==1:
        st.markdown(f"<h3 style='color:#EE7D11;'>No press releases were published during the selected date range.", unsafe_allow_html=True)
        st.markdown("---")


    st.markdown(
    """
    <a href="https://www.microbac.com/media-articles/" target="_blank" 
       style="text-decoration:none; color:#003883;">
        <p style='font-size:48px; font-weight:bold; margin:0;'>
            Microbac
        </p>
    </a>
    """,
    unsafe_allow_html=True)    
    microbac_articles = microbac_scraper()
    c = 1
    for article in microbac_articles:
        article_date = parse_date(article['date'])
        if article_date and start_date <= article_date <= end_date:
            st.markdown(f"<h3 style='color:#EE7D11;'>{c}. {article['title']}</h3>", unsafe_allow_html=True)
            st.markdown(f"**Published:** {article['date']}")
            st.markdown(f"[Read Article]({article['url']})") 
            st.markdown(f"**Description:** {article['description']}")

            st.markdown("---")
            c+=1
            save_press_releases_to_db([article])
    if c==1:
        st.markdown(f"<h3 style='color:#EE7D11;'>No press releases were published during the selected date range.", unsafe_allow_html=True)
        st.markdown("---")

# --- RSS Feed Search ---
with tab_feed:

    ai_mode = st.toggle("AI Mode", value=True, key="AI_mode", help="Enabling AI mode allows our model to filter out articles that contain your keyword, but " \
                        "that are unrelated to chemical incidents (for example, a headline about an app's 'explosion' in popularity).")

    with st.spinner("Updating feeds and archiving..."):
        filtered_articles = update_feed_and_archive(selected_rss, selected_keywords, match_type, selected_sort, ai_mode)
     
    if st.button("Run RSS Feed Search", key="rss_search"):
        pass #when the user clicks the button it refreshes the entire script so it will run rss feed search by executing the search and archive function called above
        
    # Show last updated time if there are articles
    if filtered_articles:
        tz = pytz.timezone("America/Chicago")
        last_updated = datetime.now(tz).strftime("%B %d, %Y at %I:%M:%S %p")
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
        keyword_filter = st.text_input("Keyword(s) (comma-separated)", key="archive_keyword")
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

with tab_keyword_trends:
    @st.fragment
    def keyword_trends():
        st.subheader("Reddit Volume of Mentions")
        st.info("Aggregates the number of comments from the top 1,000 Reddit posts matching the keyword over the past 12 months, and visualizes monthly engagement trends.")
        keyword_filter = st.text_input("Enter a keyword.", key="trends_keyword")

        if keyword_filter:
            status = st.empty()
            status.write(f"Analyzing monthly comment volume for **{keyword_filter}**...")
            query = keyword_filter
            months = monthly_comment_totals(query)

            fig, ax = plt.subplots()
            fig.set_size_inches(6,3)
            ax.plot(months.keys(), months.values(), marker = 'o')
            ax.set_title(f"Query: {query}", fontsize=14)
            ax.set_xlabel("Month", fontsize=10)
            ax.set_ylabel("Volume of Mentions",  fontsize=10)
            ax.tick_params(axis='x', rotation=45, labelsize=10)
            ax.tick_params(axis='y', labelsize=10)
            ax.grid(axis='y',linestyle=':')
            
            st.pyplot(fig, use_container_width=False)
            status.empty()
    keyword_trends()


with tab_settings:

    @st.fragment
    def feed_deletion():
        # st.subheader("Manage RSS Feeds")
        st.markdown("---")
        
        for feed in all_rss:
            cols = st.columns([6,1])
            cols[0].write(feed)
            if cols[1].button("Delete permanently", key=f"delete_{feed}"):

                if feed in st.session_state.user_rss_set:
                    st.session_state.user_rss_set.remove(feed)
                    remove_from_file(USER_RSS_FILE, feed)

                add_to_file(EXCLUDED_RSS_FILE, feed)
                st.success(f"Removed RSS site: {feed}")
            st.markdown("---")

    @st.fragment
    def keyword_deletion():
        # st.subheader("Manage Keywords")
        st.markdown("---")
        
        for word in all_keywords:
            cols = st.columns([6,1])
            cols[0].write(word)
            if cols[1].button("Delete permanently", key=f"delete_{word}"):

                if word in st.session_state.user_keyword_set:
                    st.session_state.user_keyword_set.remove(word)
                    remove_from_file(USER_KEYWORD_FILE, word)

                add_to_file(EXCLUDED_KEYWORDS_FILE, word)
                st.success(f"Removed keyword: {word}")

            st.markdown("---")
            
    st.info("Please refresh the page after selecting items to permanently delete for the changes to take effect.")
    with st.expander("Manage RSS Feeds"):
        feed_deletion()
    with st.expander("Manage Keywords"):
        keyword_deletion()