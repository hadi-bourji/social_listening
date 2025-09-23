from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
from datetime import datetime

def format_date(date_str):
    """Convert '05 SEP 2025' to 'September 5, 2025'"""
    try:
        date_obj = datetime.strptime(date_str, "%d %b %Y")
        return date_obj.strftime("%B %d, %Y").replace(" 0", " ")
    except:
        return date_str  

def extract_full_title(link_element, driver, base_url):
    """Extract full title by visiting the article page"""
    href = link_element.get_attribute("href")
    if href:
        full_link = urljoin(base_url, href)
        driver.execute_script("window.open(arguments[0]);", full_link)
        driver.switch_to.window(driver.window_handles[-1])
        try:
            h1 = driver.find_element(By.TAG_NAME, "h1")
            full_title = h1.text.strip()
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            return full_title
        except Exception:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
    return ""

def als_global_news_scraper():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/122.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    driver.get("https://www.alsglobal.com/en/news-and-media")

    news_items = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.columns.small-7"))
    )

    articles = []
    base_url = driver.current_url
    
    for item in news_items:
        try:
            title_link = item.find_element(By.CSS_SELECTOR, "a.n-title")
            url = title_link.get_attribute("href")
            
            if url.startswith("/"):
                url = "https://www.alsglobal.com" + url
            
            title = extract_full_title(title_link, driver, base_url)
            
            date_element = item.find_element(By.CSS_SELECTOR, "p.date")
            raw_date = date_element.text.strip() or date_element.get_attribute("textContent").strip()
            date = format_date(raw_date)
            
            description = ""
            
            if title and url:  
                articles.append({
                    "title": title,
                    "date": date,
                    "description": description,
                    "url": url
                })
        except Exception as e:
            continue

    driver.quit()
    return articles

if __name__ == "__main__":
    articles = als_global_news_scraper()
    for article in articles:
        print(f"Title: {article['title']}")
        print(f"Published Date: {article['date']}")
        print(f"URL: {article['url']}")
        print(f"Description: {article['description']}")
        print("-" * 50)