import sqlite3
from datetime import datetime
import email.utils 
import html

DB_PATH = "articles.db"

def save_articles_to_db(articles):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY,
            title TEXT,
            link TEXT UNIQUE,  -- unique constraint
            published TEXT,
            matched_keywords TEXT,
            context TEXT
        )
    ''')

    for article in articles.values():
        dt = email.utils.parsedate_to_datetime(article['Date and Time Published'])
        dt_iso = dt.strftime("%Y-%m-%d %H:%M:%S")

        context_list = [html.unescape(sentence) for sentence in article['Context']]
        context_list = list(dict.fromkeys(context_list))   
        if len(context_list) > 3:
            context_list = context_list[:3]
        
        c.execute('''
            INSERT OR IGNORE INTO articles (title, link, published, matched_keywords, context)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            article['Article Title'],
            article['Article Link'],
            dt_iso,
            ", ".join(sorted(article['Matched Keywords'])),
            " \n\n ".join(sorted(context_list))
        ))
    
    conn.commit()
    conn.close()

def query_articles(keywords=None, start_date=None, end_date=None, archive_match_type=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    query = "SELECT * FROM articles WHERE 1=1"
    params = []

    if archive_match_type=="OR":
        if keywords:
            keyword_clauses = []
            for kw in keywords:
                keyword_clauses.append("LOWER(matched_keywords) LIKE ? OR LOWER(title) LIKE ? OR LOWER(context) LIKE ? OR LOWER(link) LIKE ?")
                params.append(f"%{kw.lower()}%")
                params.append(f"%{kw.lower()}%")
                params.append(f"%{kw.lower()}%")
                params.append(f"%{kw.lower()}%")
            query += " AND (" + " OR ".join(keyword_clauses) + ")"
    elif archive_match_type=="AND":
        if keywords:
            keyword_clauses = []
            for kw in keywords:
                clause = "(" + " OR ".join([
                "LOWER(matched_keywords) LIKE ?",
                "LOWER(title) LIKE ?",
                "LOWER(context) LIKE ?",
                "LOWER(link) LIKE ?"
            ]) + ")"
                keyword_clauses.append(clause)
                params.extend([f"%{kw.lower()}%"] * 4)

            query += " AND (" + " AND ".join(keyword_clauses) + ")"

    if start_date:
        query += " AND published >= ?"
        params.append(start_date)
    if end_date:
        query += " AND published <= ?"
        params.append(end_date)

    c.execute(query, params)
    results = c.fetchall()
    conn.close()
    return results

