import sqlite3
from datetime import datetime
import email.utils 

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
        
        c.execute('''
            INSERT OR IGNORE INTO articles (title, link, published, matched_keywords, context)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            article['Article Title'],
            article['Article Link'],
            dt_iso,
            ", ".join(sorted(article['Matched Keywords'])),
            " \n\n ".join(sorted(article['Context']))
        ))
    
    conn.commit()
    conn.close()


def query_articles(keyword=None, start_date=None, end_date=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    query = "SELECT * FROM articles WHERE 1=1"
    params = []

    if keyword:
        query += " AND LOWER(matched_keywords) LIKE ?"
        params.append(f"%{keyword.lower()}%")
    
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
