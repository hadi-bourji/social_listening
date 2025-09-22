from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

def emsl_news_scraper():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/122.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    driver.get("https://emsl.com/News.aspx")

    # Wait for news items to load
    news_items = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.row[style*='display: block']"))
    )

    articles = []
    for item in news_items:
        # Get title
        title_element = item.find_element(By.CSS_SELECTOR, "p.title")
        title = title_element.get_attribute("data-abbr") or title_element.text.strip()
        
        # Get URL from the "Read More" link
        url_element = item.find_element(By.CSS_SELECTOR, "a.readmore")
        url = url_element.get_attribute("href")
        if url.startswith("News.aspx"):
            url = "https://emsl.com/" + url
        
        # Get and reformat date
        date_element = item.find_element(By.CSS_SELECTOR, "p.date")
        raw_date = date_element.get_attribute("data-abbr") or date_element.text.strip()
        
        # Convert from YYYY/MM/DD to "Month Day, Year"
        try:
            dt = datetime.strptime(raw_date, "%Y/%m/%d")
            formatted_date = dt.strftime("%B %d, %Y")  # e.g. "June 18, 2025"
        except ValueError:
            formatted_date = raw_date  # fallback if format is unexpected
        
        # Get description
        desc_element = item.find_element(By.CSS_SELECTOR, "p:not(.title):not(.author):not(.date)")
        description = desc_element.text.strip() or desc_element.get_attribute("textContent").strip()
        
        articles.append({
            "title": title,
            "date": formatted_date,
            "description": description,
            "url": url
        })

    driver.quit()
    return articles

if __name__ == "__main__":
    articles = emsl_news_scraper()
    for article in articles:
        print(f"Title: {article['title']}")
        print(f"Published Date: {article['date']}")
        print(f"URL: {article['url']}")
        print(f"Description: {article['description']}")
        print("-" * 50)
