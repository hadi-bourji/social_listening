from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def microbac_media_articles_scraper():
    url = "https://www.microbac.com/media-articles/"

    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    wait = WebDriverWait(driver, 10)
    articles = wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "a.col-12.d-flex.flex-column")
    ))

    results = []
    for a in articles:
        try:
            link = a.get_attribute("href")

            date_el = a.find_element(By.CSS_SELECTOR, "p.paragraph-lt-roman-14.mb-5")
            date_text = date_el.text.strip()
            date = date_text.split("|")[-1].strip()

            title_el = a.find_element(By.CSS_SELECTOR, "h3.paragraph-overflow-rows-2")
            title = driver.execute_script(
                "return arguments[0].childNodes[0].nodeValue.trim();", title_el
            )

            desc_el = a.find_element(By.CSS_SELECTOR, "div.paragraph-overflow-rows-2.paragraph-lt-roman-16")
            description = desc_el.text.strip()

            results.append({
                "title": title,
                "date": date,
                "description": description,
                "link": link
            })
        except Exception:
            continue

    driver.quit()
    return results


if __name__ == "__main__":
    data = microbac_media_articles_scraper()
    for d in data:
        print(d)
