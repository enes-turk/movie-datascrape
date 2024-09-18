from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class ImdbScraper:
    def __init__(self, url, headless=True):
        self.url = url
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument("--headless")
        self.options.add_argument('--lang=en-US')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        self.driver = None

    def setup_driver(self):
        try:
            self.driver = webdriver.Chrome(options=self.options)
        except Exception as e:
            print(f"Error initializing WebDriver: {e}")
            self.driver = None

    def navigate_to_page(self):
        if self.driver:
            self.driver.get(self.url)
        else:
            print("Driver is not initialized!")
    
    # TODO Implement parallel scraping to fetch multiple movie details simultaneously.
    def scrape_movie_data(self, num_titles=5):
        movie_data = []

        try:
            # Scrape movie titles and links
            self.wait_for_element((By.CSS_SELECTOR, ".ipc-page-content-container"))
            movie_title_elements = self.wait_for_elements((By.XPATH, "//div[contains(@class, 'ipc-title')]/a/h3"))
            movie_link_elements = self.wait_for_elements((By.XPATH, "//div[contains(@class, 'ipc-title')]/a"))
            movie_titles = [self.clean_movie_title(element.text) for element in movie_title_elements[:num_titles]]
            movie_links = [element.get_attribute('href') for element in movie_link_elements[:num_titles]]
            
            # Iterate over each movie
            for title, link in zip(movie_titles, movie_links):
                try:
                    # Navigate to the movie's link
                    self.driver.get(link)
                    self.scroll_to_bottom()
                    
                    # Scrape movie details
                    imdbID = link.split('/')[-2]  # Extract imdbID from the URL
                    imdbVotes = self.get_element_text((By.XPATH, "//div[@class='sc-eb51e184-3 kgbSIj']"))
                    imdbRating = self.get_element_text((By.XPATH, "//span[contains(@class, 'sc-eb51e184-1 ljxVSS')]"))
                    poster = self.get_element_attribute((By.XPATH, "//img[@class='ipc-image']"), 'src')
                    year = self.get_element_text((By.XPATH, "//ul[contains(@class, 'joVhBE baseAlt')]/li[1]"))
                    runtime = self.get_element_text((By.XPATH, "//ul[contains(@class, 'joVhBE baseAlt')]/li[3]"))
                    rated = self.get_element_text((By.XPATH, "//ul[contains(@class, 'joVhBE baseAlt')]/li[2]"))
                    director = self.get_combined_text((By.XPATH, "//ul[contains(@class, 'sc-bfec09a1-8 jZUbvq')]/li[1]/div//a"))
                    writer = self.get_combined_text((By.XPATH, "//ul[contains(@class, 'sc-bfec09a1-8 jZUbvq')]/li[2]/div//a"))
                    actors = self.get_combined_text((By.XPATH, "(//div[contains(@class, 'sc-bfec09a1-5 kdzmxK')]//a[contains(@class, 'sc-bfec09a1-1 KeEFX')])[position() <= 3]"))
                    plot = self.get_element_text((By.XPATH, "//div[contains(@class, 'sc-20579f43-0 ePKNAZ')]/div/div/div/div"))
                    genre = self.get_combined_text((By.XPATH, "//li[contains(@data-testid, 'storyline-genres')]/div/ul/li/a"))
                    country = self.get_combined_text((By.XPATH, "//li[contains(@data-testid, 'title-details-origin')]//a"))
                    released = self.get_element_text((By.XPATH, "//li[contains(@data-testid, 'title-details-releasedate')]/div/ul//a"))
                    language = self.get_combined_text((By.XPATH, "//li[contains(@data-testid, 'title-details-languages')]//a"))
                    boxOfficeBudget = self.get_element_text((By.XPATH, "//span[contains(@class, 'ipc-metadata-list-item__list-content-item') and contains(text(), '$')]"))
                    boxOfficeGross = self.get_element_text((By.XPATH, "(//span[contains(@class, 'ipc-metadata-list-item__list-content-item') and contains(text(), '$')])[4]"))

                    # Add scraped data to the movie dictionary
                    movie_data.append({
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
                    })

                    print(f"Finished: {title}")
                
                except Exception as e:
                    print(f"Error scraping movie: {link}, {str(e)}")

        except Exception as e:
            print(f"An error occurred: {e}")

        return movie_data
    
    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3.8);")
        time.sleep(1)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2.3);")
        time.sleep(1)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 1.3);")
        time.sleep(1)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
    def clean_movie_link(self, link):
        clean_link = link.split('/?')[0].strip()  # Split by '/?' and keep the part before it
        return clean_link

    def clean_movie_title(self, title):
        clean_title = title.split('. ', 1)[-1].strip()
        return clean_title
    
    def wait_for_element(self, locator, timeout=10):
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located(locator))

    def wait_for_elements(self, locator, timeout=10):
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_all_elements_located(locator))

    # Helper functions for safer scraping
    def get_element_text(self, locator):
        try:
            element = self.wait_for_element(locator)
            return element.text if element else "N/A"
        except:
            return "N/A"

    def get_element_attribute(self, locator, attribute):
        try:
            element = self.wait_for_element(locator)
            return element.get_attribute(attribute) if element else "N/A"
        except:
            return "N/A"
    
    def get_combined_text(self, locator):
        try:
            # Use wait_for_elements to get a list of elements matching the locator
            elements = self.wait_for_elements(locator)
            # Combine the text of each element into a single string, separated by commas
            return ', '.join([element.text for element in elements]) if elements else "N/A"
        except:
            return "N/A"

    def close_driver(self):
        if self.driver:
            self.driver.quit()

    def run_scraper(self):
        try:
            self.setup_driver()
            if self.driver:
                self.navigate_to_page()
                data = self.scrape_movie_data()
                return data
            else:
                print("Driver failed to initialize.")
                return []
        finally:
            self.close_driver()