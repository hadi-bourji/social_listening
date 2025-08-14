Environmental Emergency News Monitor
This is a Streamlit-based RSS feed monitoring tool that scans multiple news sources for environmental emergency incidents and displays relevant articles based on user-defined keywords.
It’s designed to help teams quickly identify incidents like chemical spills, industrial accidents, hazardous waste releases, and other environmental hazards across the U.S.


Features:

Multiple RSS Feeds – Accepts a list of RSS feed URLs from national and local news outlets.

Keyword Filtering – Finds only articles containing specified environmental incident terms.

Context Extraction – Shows up to three key sentence excerpts where keywords are found.

Duplicate Removal – Removes exact duplicates and filters out international news (non-U.S.).


Sorting Options:

None (default)

Published Date (Newest First)

Number of Keywords Matched (Most)


Time Zone Handling – Converts published times to U.S. Central Time.

Auto-Refresh – Refreshes the feed periodically to capture new articles.

Clean Display – Titles, publish times, source links, matched keywords, and contextual sentences.


Installation:

Clone the Repository
git clone https://github.com/yourusername/environmental-emergency-monitor.git
cd environmental-emergency-monitor

Install Dependencies
pip install -r requirements.txt
Usage

Run the Streamlit app:
streamlit run app.py


App Workflow

User Inputs:

RSS Feed URLs – One per line, covering your preferred U.S. news sources.

Keywords – One per line, describing environmental emergencies to track.

Article Extraction:

Fetches all articles from provided feeds.

Extracts title, summary, link, published, and content when available.

Filtering:

Uses regex to match exact keywords (case-insensitive).

Captures surrounding sentences for context (up to 3).

Removes duplicates and any articles mentioning excluded countries (e.g., France, UK, Russia).

Display:

Lists relevant articles with:

Title

Published Time (Central Time)

Matched Keywords

Up to 3 contextual excerpts

Example Keywords
oil spill
chemical leak
hazardous waste
industrial accident
pipeline leak
toxic release
groundwater contamination


File Structure
app.py                 # Main Streamlit application
requirements.txt       # Python dependencies
Eurofins.png           # Logo displayed in app
README.md              # Documentation


Key Functions
extract_articles() – Retrieves and parses RSS feed content.

get_relevant_articles() – Filters and extracts relevant articles with matched keywords.

remove_exact_duplicates() – Removes duplicates and filters out non-U.S. incidents.

replace_tag_with_boundary() – Ensures HTML tags don't break sentence detection.


Dependencies
streamlit

feedparser

pytz

python-dateutil

streamlit-autorefresh


Install all via:
pip install -r requirements.txt


Future Improvements
Add state-specific filtering for more localized alerts.

Integrate email/SMS alerts for high-priority incidents.

Store past alerts in a database for historical reference.

