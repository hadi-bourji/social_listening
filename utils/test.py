from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def gel_scraper():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/122.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    driver.get("https://www.gel.com/blog")

    # Wait for all article anchors to load
    news_items = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.m-result-item-filtered-list"))
    )

    # Wait for the first headline to have non-empty text
    WebDriverWait(driver, 10).until(
        lambda d: d.find_elements(By.CSS_SELECTOR, "h2.m-result-item-filtered-list__headline")[0].text.strip() != ""
    )

    articles = []
    for item in news_items:
        try:
            url = item.get_attribute("href")

            title_element = item.find_element(By.CSS_SELECTOR, "h2.m-result-item-filtered-list__headline")
            title = title_element.text.strip()

            desc_element = item.find_element(By.CSS_SELECTOR, "p.m-result-item-filtered-list__summary")
            description = desc_element.text.strip()

            date_element = item.find_element(By.CSS_SELECTOR, "time")
            date = date_element.get_attribute("datetime") or date_element.text.strip()

            articles.append({
                "title": title,
                "date": date,
                "description": description,
                "url": url
            })
        except Exception as e:
            print(f"Error parsing item: {e}")
            continue

    driver.quit()
    return articles
if __name__ == "__main__":
    # articles = epa_scraper()
    # articles = pacelabs_scraper()
    # articles = sgs_scraper()
    articles = gel_scraper()
    for article in articles:
        print(f"Title: {article['title']}\nPublished Date: {article['date']}\nURL: {article['url']}\nDescription: {article['description']}\n")