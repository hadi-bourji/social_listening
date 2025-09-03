# Environmental Emergency News Monitor

This is a Streamlit-based RSS feed monitoring tool that scans multiple news sources for environmental emergency incidents and displays relevant articles based on user-defined keywords.
It’s designed to help teams quickly identify incidents like chemical spills, industrial accidents, hazardous waste releases, and other environmental hazards across the U.S.

## Features

- Multiple RSS Feeds – Accepts a list of RSS feed URLs from national and local news outlets.
- Keyword Filtering – Finds only articles containing specified environmental incident terms.
- Context Extraction – Shows up to three key sentence excerpts where keywords are found.
- Duplicate Removal – Removes exact duplicates and filters out international news (non-U.S.).
- Archive Current Results – Saves the latest fetched articles for historical reference.  
- Search Archive – Allows searching past articles by keywords and date range.  
- Optional ML Classifier Mode – Applies a machine learning model after keyword filtering to ensure articles are truly relevant to environmental emergencies.


### Sorting Options

- None (default)
- Published Date (Newest First)
- Number of Keywords Matched (Most)

### Additional Features

- Time Zone Handling – Converts published times to U.S. Central Time.
- Auto-Refresh – Refreshes the feed periodically to capture new articles.
- Clean Display – Titles, publish times, source links, matched keywords, and contextual sentences.

## Installation

#### Clone the Repository:    
git clone https://github.com/hadi-bourji/social_listening.git  
cd environmental-emergency-monitor  

#### Install Dependencies:    
pip install -r requirements.txt  

#### Run the Streamlit app:  
streamlit run script.py



## App Workflow

### User Inputs

- RSS Feed URLs – One per line, covering your preferred news sources.
- Keywords – One per line, describing topics you would like to track.

### Article Extraction

- Fetches all articles from provided feeds.
- Extracts title, summary, link, published, and content when available.

### Filtering

- Uses regex to match exact keywords (case-insensitive).
- Captures surrounding sentences for context (up to 3).
- Removes duplicates and any articles mentioning excluded countries (e.g., France, UK, Russia).
- Optional ML Classifier Mode – If enabled, articles passing keyword filters are further screened by a trained classifier to reduce false positives.


### Display

Lists relevant articles with:

- Title
- Published Time (Central Time)
- Matched Keywords
- Up to 3 contextual excerpts

### Archive Current Results  
- Save all currently fetched and filtered articles.  
- Each archived entry stores:
  - Title
  - Published Date
  - Source
  - Matched Keywords
  - Contextual Sentences

### Search Through the Archive  
- Search archived articles by **keywords**.  
- Filter articles by **date range** to find incidents between specific start and end dates.  
- Returns a list of matching articles with:
  - Title
  - Published Date
  - Source
  - Matched Keywords
  - Up to 3 contextual sentences

This feature makes it easy to **analyze trends over time**, revisit past incidents, or generate reports for specific environmental hazards.

## Example Keywords

- oil spill
- chemical leak
- hazardous waste
- industrial accident
- pipeline leak
- toxic release
- groundwater contamination

## File Structure

- script.py              # Main Streamlit application
- requirements.txt       # Python dependencies
- README.md              # Documentation

## Key Functions

- extract_articles() – Retrieves and parses RSS feed content.
- get_relevant_articles() – Filters and extracts relevant articles with matched keywords.
- remove_exact_duplicates() – Removes duplicates and filters out non-U.S. incidents.
- replace_tag_with_boundary() – Ensures HTML tags don't break sentence detection.

## Dependencies

- streamlit
- feedparser
- pytz
- python-dateutil
- streamlit-autorefresh

Install all via:
pip install -r requirements.txt



## Future Improvements


- Integrate email/SMS alerts for high-priority incidents.