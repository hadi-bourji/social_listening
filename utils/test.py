from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from urllib.parse import urljoin
from datetime import datetime

from selenium.common.exceptions import StaleElementReferenceException

def montrose_scraper():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=options)

    driver.get("https://montrose-env.com/news-events/")

    # Wait for grid items to load
    news_items = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.vc_grid-item"))
    )

    articles = []
    for item in news_items:
        try:
            # Refetch elements inside a retry block to avoid stale references
            link_element = item.find_element(By.CSS_SELECTOR, "a")
            url = link_element.get_attribute("href")

            title_element = item.find_element(By.CSS_SELECTOR, "h4")
            title = title_element.text.strip() or title_element.get_attribute("textContent").strip()

            desc_element = item.find_element(By.CSS_SELECTOR, ".vc_gitem-post-data-source-post_excerpt")
            description = desc_element.text.strip() or desc_element.get_attribute("textContent").strip()

            date_element = item.find_element(By.CSS_SELECTOR, ".vc_gitem-post-data-source-post_date")
            date = date_element.text.strip() or date_element.get_attribute("textContent").strip()

            articles.append({
                "title": title,
                "date": date,
                "description": description,
                "url": url
            })
        except StaleElementReferenceException:
            # If stale, refetch the item from the DOM and retry
            try:
                refreshed_item = driver.find_element(By.XPATH, f"//div[contains(@class,'vc_grid-item') and .//a[@href='{url}']]")
                link_element = refreshed_item.find_element(By.CSS_SELECTOR, "a")
                url = link_element.get_attribute("href")

                title_element = refreshed_item.find_element(By.CSS_SELECTOR, "h4")
                title = title_element.text.strip() or title_element.get_attribute("textContent").strip()

                desc_element = refreshed_item.find_element(By.CSS_SELECTOR, ".vc_gitem-post-data-source-post_excerpt")
                description = desc_element.text.strip() or desc_element.get_attribute("textContent").strip()

                date_element = refreshed_item.find_element(By.CSS_SELECTOR, ".vc_gitem-post-data-source-post_date")
                date = date_element.text.strip() or date_element.get_attribute("textContent").strip()

                articles.append({
                    "title": title,
                    "date": date,
                    "description": description,
                    "url": url
                })
            except Exception:
                continue

    driver.quit()
    return articles




if __name__ == "__main__":
    data = montrose_scraper()
    for d in data:
        print(d)
