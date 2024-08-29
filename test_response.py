import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def scrape_imdb_top_250():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        url = 'https://www.imdb.com/chart/top/?ref_=nv_mv_250'
        driver.get(url)
        print(f"Navigated to {url}")

        # Wait for any element to be present to ensure page has started loading
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("Page body loaded")

        # Scroll to bottom of page to trigger any lazy loading
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # Wait for potential lazy loading

        try:
            title_elements = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, "//li[@class='ipc-metadata-list-summary-item']//h3[@class='ipc-title__text']"))
            )
            print(f"Found {len(title_elements)} title elements")
        except TimeoutException:
            print("Timeout while waiting for title elements. Trying alternative XPath...")
            title_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'ipc-title')]/a/h3")
            print(f"Found {len(title_elements)} title elements with alternative XPath")

        if not title_elements:
            print("No title elements found. Printing page source:")
            print(driver.page_source)
            return

        titles = []
        for title_element in title_elements:
            title = title_element.text
            clean_title = title.split('. ', 1)[-1].strip() if '. ' in title else title
            titles.append(clean_title)

        print(f"Scraped {len(titles)} movie titles")
        
        for i, title in enumerate(titles, 1):
            print(f"{i}. {title}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_imdb_top_250()