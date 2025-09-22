from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

def babcock_news_scraper():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/122.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    driver.get("https://www.babcock.com/home/about/corporate/news")

    wait = WebDriverWait(driver, 15)

    news_items = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.box-news-item"))
    )

    articles = []
    for item in news_items:
        # Title
        try:
            title_element = item.find_element(By.CSS_SELECTOR, "h2.text-heading a")
            title = title_element.text.strip()
            url = title_element.get_attribute("href")
        except:
            # Fallback: use the "Read More" link
            title = ""
            try:
                url = item.find_element(By.CSS_SELECTOR, "a.brand-button-blue").get_attribute("href")
            except:
                url = ""

        if url.startswith("/"):
            url = "https://www.babcock.com" + url

        # Date
        try:
            raw_date = item.find_element(By.CSS_SELECTOR, "p.text-news-date").text.strip()
            dt = datetime.strptime(raw_date, "%B %d, %Y")
            formatted_date = dt.strftime("%B %d, %Y")
        except:
            formatted_date = ""

        # Description
        try:
            description = item.find_element(By.CSS_SELECTOR, "div.text-news-body div.mb-4").text.strip()
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
    articles = babcock_news_scraper()
    for article in articles:
        print(f"Title: {article['title']}")
        print(f"Published Date: {article['date']}")
        print(f"URL: {article['url']}")
        print(f"Description: {article['description']}")
        print("-" * 50)
