from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from urllib.parse import urljoin
from datetime import datetime

def babcock_scraper():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=options)

    # Replace with actual Babcock Laboratories news URL
    driver.get("https://www.babcocklabs.com/news")  # Update this URL

    # Wait for article items to load
    news_items = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.entry.h-entry.hentry"))
    )

    articles = []
    for item in news_items:
        try:
            # Extract title from h1
            title_element = item.find_element(By.CSS_SELECTOR, "h1.entry-title a")
            title = title_element.text.strip()
            url = title_element.get_attribute("href")

            # Extract date from time element
            date_element = item.find_element(By.CSS_SELECTOR, "time.dt-published")
            date = date_element.get_attribute("datetime")  # Gets ISO format date
            
            # Extract description from summary div
            try:
                desc_element = item.find_element(By.CSS_SELECTOR, "div.p-summary p")
                description = desc_element.text.strip()
            except:
                description = ""

            # Extract author
            try:
                author_element = item.find_element(By.CSS_SELECTOR, "span.entry-author a")
                author = author_element.text.strip()
            except:
                author = ""

            # Extract category
            try:
                category_element = item.find_element(By.CSS_SELECTOR, "span.entry-category a")
                category = category_element.text.strip()
            except:
                category = ""

            articles.append({
                "title": title,
                "date": date,
                "description": description,
                "url": url
            })
        except StaleElementReferenceException:
            # Retry if element becomes stale
            try:
                refreshed_items = driver.find_elements(By.CSS_SELECTOR, "article.entry.h-entry.hentry")
                for refreshed_item in refreshed_items:
                    try:
                        title_element = refreshed_item.find_element(By.CSS_SELECTOR, "h1.entry-title a")
                        current_url = title_element.get_attribute("href")
                        if current_url == url:
                            # Already processed
                            break
                    except:
                        continue
            except Exception:
                continue
        except Exception as e:
            print(f"Error processing article: {e}")
            continue

    driver.quit()
    return articles


if __name__ == "__main__":
    data = babcock_scraper()
    for d in data:
        print(d)
        print("-" * 80)