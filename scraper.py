from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

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

    def wait_for_element(self, locator, timeout=30):
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located(locator))

    def wait_for_elements(self, locator, timeout=30):
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_all_elements_located(locator))
    
    def clean_movie_title(self, title):
        clean_title = title.split('. ', 1)[-1].strip()
        return clean_title

    def scrape_movie_titles(self, num_titles=10):
        try:
            # Wait for the page to load
            self.wait_for_element((By.CSS_SELECTOR, ".ipc-page-content-container"))
            
            # Wait for the movie title elements
            movie_title_elements = self.wait_for_elements((By.XPATH, "//div[contains(@class, 'ipc-title')]/a/h3"))
            
            # Wait for the movie link elements
            movie_link_elements = self.wait_for_elements((By.XPATH, "//div[contains(@class, 'ipc-title')]/a"))

            # Scrape movie titles
            movie_titles = [self.clean_movie_title(element.text) for element in movie_title_elements[:num_titles]]
            
            # Scrape movie links (getting the href attribute)
            movie_links = [element.get_attribute('href') for element in movie_link_elements[:num_titles]]
            
            # Prepare movie_data containing titles and links
            movie_data = [{'title': title, 'link': link} for title, link in zip(movie_titles, movie_links)]

            return movie_data

        except Exception as e:
            print(f"An error occurred: {e}")
            return []
    
    def scrape_movie_data(self):
        try:
            movie_data = self.scrape_movie_titles()
            if not movie_data:
                print("No movie data to scrape.")
                return movie_data

            # Loop through each movie's data
            for movie in movie_data:
                # Navigate to the movie's link
                self.driver.get(movie['link'])
                
                # Wait for the page to load (adjust this as needed based on page structure)
                self.wait_for_element((By.XPATH, "//span[contains(@class, 'sc-eb51e184-1 ljxVSS')]"))

                # Scrape the IMDb rating
                rating_element = self.wait_for_element((By.XPATH, "//span[contains(@class, 'sc-eb51e184-1 ljxVSS')]"))
                imdb_rating = rating_element.text if rating_element else "N/A"
                
                # Add IMDb rating to the movie data
                movie['imdb_rating'] = imdb_rating

            return movie_data

        except Exception as e:
            print(f"An error occurred while scraping movie data: {e}")
            return movie_data
        

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