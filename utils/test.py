from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def gel_blog_scraper():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/122.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    driver.get("https://www.gel.com/blog")

    news_items = WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.space-y-5.md\\:flex")))

    articles = []
    for item in news_items:
        url_element = item.find_element(By.CSS_SELECTOR, "h2 a")
        url = url_element.get_attribute("href")
        
        title = url_element.text.strip() or url_element.get_attribute("textContent").strip()
        
        date_element = item.find_element(By.CSS_SELECTOR, "div.text-body-xs span")
        date = date_element.text.strip() or date_element.get_attribute("textContent").strip()
        
        desc_elements = item.find_elements(By.CSS_SELECTOR, "p")
        description = ""
        for p in desc_elements:
            text = p.text.strip() or p.get_attribute("textContent").strip()
            if text and len(text) > 10:  
                description = text
                break
        
        articles.append({
            "title": title,
            "date": date,
            "description": description,
            "url": url
        })

    driver.quit()
    return articles

if __name__ == "__main__":
    articles = gel_blog_scraper()
    for article in articles:
        print(f"Title: {article['title']}\nPublished Date: {article['date']}\nURL: {article['url']}\nDescription: {article['description']}\n")