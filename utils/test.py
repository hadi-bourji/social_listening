from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

def wecklabs_news_scraper():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/122.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    driver.get("https://www.wecklabs.com/Company/SocialNetworking/News.aspx")

    wait = WebDriverWait(driver, 15)
    news_items = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.BlogBody"))
    )

    articles = []
    for item in news_items:
        # Title + URL
        try:
            title_element = item.find_element(By.CSS_SELECTOR, "h2.BlogTitle a")
            title = title_element.text.strip()
            url = title_element.get_attribute("href")
        except:
            title = ""
            url = ""

        # Date (convert to "Month Day, Year" format)
        try:
            date_element = item.find_element(By.CSS_SELECTOR, "span.BlogDateline:nth-of-type(2)")
            raw_date = date_element.text.strip()  # e.g., "9/17/2025 10:00 AM"
            dt = datetime.strptime(raw_date, "%m/%d/%Y %I:%M %p")
            formatted_date = dt.strftime("%B %d, %Y")
        except:
            formatted_date = ""

        # Description (first <p> inside main div)
        try:
            desc_element = item.find_element(By.CSS_SELECTOR, "div[style*='padding-top'] p")
            description = desc_element.text.strip()
        except:
            description = ""

        articles.append({
            "title": title,
            "date": formatted_date,
            "description": description,
            "url": url
        })

    driver.quit()
    return articles


if __name__ == "__main__":
    articles = wecklabs_news_scraper()
    for article in articles:
        print(f"Title: {article['title']}")
        print(f"Published Date: {article['date']}")
        print(f"URL: {article['url']}")
        print(f"Description: {article['description']}")
        print("-" * 50)
