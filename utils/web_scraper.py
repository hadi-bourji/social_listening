from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def epa_scraper():
    # Scrapes EPA press release site. Returns each article title, date published, description, and the article URL.
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
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

        articles.append({
        "title": title,
        "date": date,
        "description": description,
        "url": url})

    driver.quit()
    return articles


def pacelabs_scraper():
    # Scrapes pacelabs press release site. Returns each article title, date published, description, and the article URL.
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
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


def sgs_scraper():
    options = Options()
    options.add_argument("--headless=new")
    #sgs was detecting a bot, make the browser look more human
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/122.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    driver.get("https://www.sgs.com/en/news")

    # Wait for all article anchors
    news_items = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.m-result-item-filtered-list"))
    )
    # Wait for text content to be populated
    WebDriverWait(driver, 10).until(
        lambda driver: driver.find_elements(By.CSS_SELECTOR, "h2.m-result-item-filtered-list__headline")[0].text.strip() != ""
    )            

    articles = []
    for item in news_items:

        title_element = item.find_element(By.CSS_SELECTOR, "h2.m-result-item-filtered-list__headline")
        title = title_element.text.strip() or title_element.get_attribute("textContent").strip()
        
        description_element = item.find_element(By.CSS_SELECTOR, "div.m-result-item-filtered-list__description")
        description = description_element.text.strip() or description_element.get_attribute("textContent").strip()
        
        date_elements = item.find_elements(By.CSS_SELECTOR, "dl.m-result-item-filtered-list__metadata dd")
        date = ""
        if date_elements:
            date = date_elements[-1].text.strip() or date_elements[-1].get_attribute("textContent").strip()
            


        url = item.get_attribute("href")

        articles.append({
            "title": title,
            "date": date,
            "description": description,
            "url": url
        })

    driver.quit()
    return articles


def montrose_scraper():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/122.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    driver.get("https://montrose-env.com/news-events/")

    # Wait for grid items to load
    news_items = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.vc_grid-item"))
    )

    articles = []
    for item in news_items:
     
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
            
      

    driver.quit()
    return articles


if __name__ == "__main__":
    # articles = epa_scraper()
    # articles = pacelabs_scraper()
    # articles = sgs_scraper()
    articles = montrose_scraper()
    for article in articles:
        print(f"Title: {article['title']}\nPublished Date: {article['date']}\nURL: {article['url']}\nDescription: {article['description']}\n")