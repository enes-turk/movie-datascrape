from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import logging
from queue import Queue

class ImdbScraper:
    def __init__(self, url, headless=True, num_workers=5):
        self.url = url
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument("--headless")
        self.options.add_argument('--lang=en-US')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        self.num_workers = num_workers
        self.driver_pool = Queue()
        self.setup_driver_pool()

    def setup_driver_pool(self):
        for _ in range(self.num_workers):
            driver = webdriver.Chrome(options=self.options)
            self.driver_pool.put(driver)

    def get_driver(self):
        return self.driver_pool.get()

    def release_driver(self, driver):
        self.driver_pool.put(driver)

    def scrape_movie_data(self, num_titles=20):
        movie_data = []
        scraped_movies = set()  # To keep track of scraped movies

        try:
            driver = self.get_driver()
            driver.get(self.url)
            self.wait_for_element(driver, (By.CSS_SELECTOR, ".ipc-page-content-container"))
            movie_title_elements = self.wait_for_elements(driver, (By.XPATH, "//div[contains(@class, 'ipc-title')]/a/h3"))
            movie_link_elements = self.wait_for_elements(driver, (By.XPATH, "//div[contains(@class, 'ipc-title')]/a"))
            movie_titles = [self.clean_movie_title(element.text) for element in movie_title_elements[:num_titles]]
            movie_links = [element.get_attribute('href') for element in movie_link_elements[:num_titles]]
            self.release_driver(driver)

            with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                future_to_movie = {executor.submit(self.scrape_single_movie, title, link): (title, link) for title, link in zip(movie_titles, movie_links)}
                for future in as_completed(future_to_movie):
                    title, link = future_to_movie[future]
                    try:
                        data = future.result()
                        if data and data['imdbID'] not in scraped_movies:
                            movie_data.append(data)
                            scraped_movies.add(data['imdbID'])
                            logging.info(f"Finished: {title}")
                    except Exception as e:
                        logging.error(f"Error scraping movie: {link}, {str(e)}")

        except Exception as e:
            logging.error(f"An error occurred: {e}")

        return movie_data

    def scrape_single_movie(self, title, link):
        driver = self.get_driver()
        try:
            driver.get(link)
            self.scroll_to_bottom(driver)
            
            imdbID = link.split('/')[-2]
            imdbVotes = self.get_element_text(driver, (By.XPATH, "//div[@class='sc-eb51e184-3 kgbSIj']"))
            imdbRating = self.get_element_text(driver, (By.XPATH, "//span[contains(@class, 'sc-eb51e184-1 ljxVSS')]"))
            poster = self.get_element_attribute(driver, (By.XPATH, "//img[@class='ipc-image']"), 'src')
            year = self.get_element_text(driver, (By.XPATH, "//ul[contains(@class, 'joVhBE baseAlt')]/li[1]"))
            runtime = self.get_element_text(driver, (By.XPATH, "//ul[contains(@class, 'joVhBE baseAlt')]/li[3]"))
            rated = self.get_element_text(driver, (By.XPATH, "//ul[contains(@class, 'joVhBE baseAlt')]/li[2]"))
            director = self.get_combined_text(driver, (By.XPATH, "//ul[contains(@class, 'sc-bfec09a1-8 jZUbvq')]/li[1]/div//a"))
            writer = self.get_combined_text(driver, (By.XPATH, "//ul[contains(@class, 'sc-bfec09a1-8 jZUbvq')]/li[2]/div//a"))
            actors = self.get_combined_text(driver, (By.XPATH, "(//div[contains(@class, 'sc-bfec09a1-5 kdzmxK')]//a[contains(@class, 'sc-bfec09a1-1 KeEFX')])[position() <= 3]"))
            plot = self.get_element_text(driver, (By.XPATH, "//div[contains(@class, 'sc-20579f43-0 ePKNAZ')]/div/div/div/div"))
            genre = self.get_combined_text(driver, (By.XPATH, "//li[contains(@data-testid, 'storyline-genres')]/div/ul/li/a"))
            country = self.get_combined_text(driver, (By.XPATH, "//li[contains(@data-testid, 'title-details-origin')]//a"))
            released = self.get_element_text(driver, (By.XPATH, "//li[contains(@data-testid, 'title-details-releasedate')]/div/ul//a"))
            language = self.get_combined_text(driver, (By.XPATH, "//li[contains(@data-testid, 'title-details-languages')]//a"))
            boxOfficeBudget = self.get_element_text(driver, (By.XPATH, "//span[contains(@class, 'ipc-metadata-list-item__list-content-item') and contains(text(), '$')]"))
            boxOfficeGross = self.get_element_text(driver, (By.XPATH, "(//span[contains(@class, 'ipc-metadata-list-item__list-content-item') and contains(text(), '$')])[4]"))

            return {
                'Title': title,
                'imdbRating': imdbRating,
                'Year': year,
                'Runtime': runtime,
                'Rated': rated,
                'Released': released,
                'Genre': genre,
                'Director': director,
                'Writer': writer,
                'Actors': actors,
                'Plot': plot,
                'Language': language,
                'Country': country,
                'Poster': poster,
                'imdbVotes': imdbVotes,
                'imdbID': imdbID,
                'BoxOfficeBudget': boxOfficeBudget,
                'BoxOfficeGross': boxOfficeGross
            }

        finally:
            self.release_driver(driver)
    
    def scroll_to_bottom(self, driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3.8);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2.3);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 1.3);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                  
    def clean_movie_link(self, link):
        clean_link = link.split('/?')[0].strip()
        return clean_link

    def clean_movie_title(self, title):
        clean_title = title.split('. ', 1)[-1].strip()
        return clean_title
    
    def wait_for_element(self, driver, locator, timeout=10):
        wait = WebDriverWait(driver, timeout)
        return wait.until(EC.presence_of_element_located(locator))

    def wait_for_elements(self, driver, locator, timeout=10):
        wait = WebDriverWait(driver, timeout)
        return wait.until(EC.presence_of_all_elements_located(locator))

    def get_element_text(self, driver, locator):
        try:
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            return element.text if element else "N/A"
        except:
            return "N/A"

    def get_element_attribute(self, driver, locator, attribute):
        try:
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            return element.get_attribute(attribute) if element else "N/A"
        except:
            return "N/A"
    
    def get_combined_text(self, driver, locator):
        try:
            elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
            return ', '.join([element.text for element in elements]) if elements else "N/A"
        except:
            return "N/A"

    def close_all_drivers(self):
        while not self.driver_pool.empty():
            driver = self.driver_pool.get()
            driver.quit()

    def run_scraper(self):
        try:
            data = self.scrape_movie_data()
            return data
        finally:
            self.close_all_drivers()