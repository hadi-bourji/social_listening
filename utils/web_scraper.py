from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def epa_scrape():
    # Scrapes EPA press release site. Returns each article title, date published, description, and the article URL.
    driver = webdriver.Chrome()
    driver.get("https://www.epa.gov/newsreleases/search")

    wait = WebDriverWait(driver, 10)
    news_items = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.usa-collection__item")))
    
    articles = []

    for item in news_items:
        link_elem = item.find_element(By.CSS_SELECTOR, "h3.usa-collection__heading a")
        title = item.find_element(By.CSS_SELECTOR, "h3.usa-collection__heading a").text
        date = item.find_element(By.CSS_SELECTOR, "time").text
        descriptions = item.find_elements(By.CSS_SELECTOR, "p.usa-collection__description")
        descriptions = [desc.text.strip() for desc in descriptions if desc.text.strip()]
        description = " ".join(descriptions) if descriptions else "No description available"
        url = link_elem.get_attribute("href")

        print(f"{date} - {title}\nURL: {url}\n{description}\n")
        articles.append({
        "title": title,
        "date": date,
        "description": description,
        "url": url})

    driver.quit()
    return articles

if __name__ == "__main__":
    articles = epa_scrape()
    for article in articles:
        print(f"Title: {article['title']}\nPublished Date: {article['date']}\nURL: {article['url']}\n{article['description']}\n")
