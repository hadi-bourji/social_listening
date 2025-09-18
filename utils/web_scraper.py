from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def epa_scraper():
    # Scrapes EPA press release site. Returns each article title, date published, description, and the article URL.
    driver = webdriver.Chrome()
    driver.get("https://www.epa.gov/newsreleases/search")

    news_items = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.usa-collection__item")))
    
    articles = []

    for item in news_items:
        link_elem = item.find_element(By.CSS_SELECTOR, "h3.usa-collection__heading a")
        title = item.find_element(By.CSS_SELECTOR, "h3.usa-collection__heading a").text
        date = item.find_element(By.CSS_SELECTOR, "time").text
        descriptions = item.find_elements(By.CSS_SELECTOR, "p.usa-collection__description")
        descriptions = [desc.text.strip() for desc in descriptions if desc.text.strip()]
        description = " ".join(descriptions) if descriptions else "No description available"
        url = link_elem.get_attribute("href")

        # print(f"{date} - {title}\nURL: {url}\n{description}\n")
        articles.append({
        "title": title,
        "date": date,
        "description": description,
        "url": url})

    driver.quit()
    return articles


def pacelabs_scraper():
    driver = webdriver.Chrome()
    driver.get("https://www.pacelabs.com/company/press-releases-and-articles/")
    
    wrapper = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.uc_post_grid_style_one_wrap.ue_post_grid.uc-items-wrapper")))

    news_items = wrapper.find_elements(By.CSS_SELECTOR, "div.uc_post_grid_style_one_item.ue_post_grid_item")

    articles = []

    for item in news_items:
        title_elem = item.find_elements(By.CSS_SELECTOR, ".uc_post_title a div")
        title = title_elem[0].text.strip() if title_elem else "No title"

        url_elem = item.find_elements(By.CSS_SELECTOR, ".uc_post_title a")
        url = url_elem[0].get_attribute("href") if url_elem else "No URL"

        date_elem = item.find_elements(By.CSS_SELECTOR, ".ue-grid-item-meta-data")
        date = date_elem[0].text.strip() if date_elem else "No date"

        desc_elem = item.find_elements(By.CSS_SELECTOR, ".uc_post_text")
        description = desc_elem[0].text.strip() if desc_elem else "No description"

        articles.append({
            "title": title,
            "date": date,
            "description": description,
            "url": url
        })

    driver.quit()
    return articles


if __name__ == "__main__":
    articles = epa_scraper()
    articles = pacelabs_scraper()
    for article in articles:
        print(f"Title: {article['title']}\nPublished Date: {article['date']}\nURL: {article['url']}\n{article['description']}\n")
    
