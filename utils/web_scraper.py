from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime

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

def gel_scraper():
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


def emsl_scraper():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/122.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    driver.get("https://emsl.com/News.aspx")

    news_items = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.row[style*='display: block']"))
    )

    articles = []
    for item in news_items:
        title_element = item.find_element(By.CSS_SELECTOR, "p.title")
        title = title_element.get_attribute("data-abbr") or title_element.text.strip()
        
        url_element = item.find_element(By.CSS_SELECTOR, "a.readmore")
        url = url_element.get_attribute("href")
        if url.startswith("News.aspx"):
            url = "https://emsl.com/" + url
        
        date_element = item.find_element(By.CSS_SELECTOR, "p.date")
        raw_date = date_element.get_attribute("data-abbr") or date_element.text.strip()
        
        try:
            dt = datetime.strptime(raw_date, "%Y/%m/%d")
            formatted_date = dt.strftime("%B %d, %Y")  
        except ValueError:
            formatted_date = raw_date 
        
        desc_element = item.find_element(By.CSS_SELECTOR, "p:not(.title):not(.author):not(.date)")
        description = desc_element.text.strip() or desc_element.get_attribute("textContent").strip()
        
        articles.append({
            "title": title,
            "date": formatted_date,
            "description": description,
            "url": url
        })

    driver.quit()
    return articles

def babcock_scraper():
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
        
        try:
            title_element = item.find_element(By.CSS_SELECTOR, "h2.text-heading a")
            title = title_element.text.strip()
            url = title_element.get_attribute("href")
        except:
            title = ""
            try:
                url = item.find_element(By.CSS_SELECTOR, "a.brand-button-blue").get_attribute("href")
            except:
                url = ""

        if url.startswith("/"):
            url = "https://www.babcock.com" + url

        try:
            raw_date = item.find_element(By.CSS_SELECTOR, "p.text-news-date").text.strip()
            dt = datetime.strptime(raw_date, "%B %d, %Y")
            formatted_date = dt.strftime("%B %d, %Y")
        except:
            formatted_date = ""

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

def wecklabs_scraper():
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
    # articles = epa_scraper()
    # articles = pacelabs_scraper()
    # articles = sgs_scraper()
    # articles = montrose_scraper()
    # articles = gel_scraper()
    # articles = emsl_scraper()
    articles = wecklabs_scraper()
    for article in articles:
        print(f"Title: {article['title']}\nPublished Date: {article['date']}\nURL: {article['url']}\nDescription: {article['description']}\n")