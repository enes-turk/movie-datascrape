from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
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

    def scrape_movie_titles(self, num_titles=1):
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
            movie_data = [{'Title': title, 'Link': link} for title, link in zip(movie_titles, movie_links)]

            return movie_data

        except Exception as e:
            print(f"An error occurred: {e}")
            return []
    
    def scrape_movie_data(self):
        movie_data = self.scrape_movie_titles()
        for movie in movie_data:
            try:
                # Navigate to the movie's link
                self.driver.get(movie['Link'])
                
                # self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.scroll_slowly()
                
                # Wait for the page to load (adjust wait time based on page load speed)
                self.wait_for_element((By.XPATH, "//span[contains(@class, 'sc-eb51e184-1 ljxVSS')]"))

                # Scrape IMDb rating
                imdbRating = self.get_element_text((By.XPATH, "//span[contains(@class, 'sc-eb51e184-1 ljxVSS')]"))

                # Scrape year of release
                year = self.get_element_text((By.XPATH, "//ul[contains(@class, 'joVhBE baseAlt')]/li[1]"))

                # Scrape runtime
                runtime = self.get_element_text((By.XPATH, "//ul[contains(@class, 'joVhBE baseAlt')]/li[3]"))

                # Scrape additional movie details
                rated = self.get_element_text((By.XPATH, "//ul[contains(@class, 'joVhBE baseAlt')]/li[2]"))
                released = self.get_element_text((By.XPATH, "//li[contains(@data-testid, 'title-details-releasedate')]/div/ul//a"))
                genre = self.get_combined_text((By.XPATH, "//li[contains(@data-testid, 'storyline-genres')]/div/ul/li/a"))
                director = self.get_combined_text((By.XPATH, "//ul[contains(@class, 'sc-bfec09a1-8 jZUbvq')]/li[1]/div//a"))
                # writer = self.get_element_text((By.XPATH, "//a[contains(@href, '/name/nm')][2]"))
                # actors = self.get_element_text((By.XPATH, "//a[contains(@href, '/name/nm')][3]"))
                # plot = self.get_element_text((By.XPATH, "//span[@class='GenresAndPlot__TextContainerBreakpointXL-cum89p-2 gCtawA']"))
                # language = self.get_element_text((By.XPATH, "//a[contains(@href, '/search/title?languages')]"))
                # country = self.get_element_text((By.XPATH, "//a[contains(@href, '/search/title?countries')]"))
                # awards = self.get_element_text((By.XPATH, "//span[contains(@class, 'ipc-metadata-list-item__label') and text()='Awards']"))
                # poster = self.get_element_attribute((By.XPATH, "//img[@class='ipc-image']"), 'src')
                # imdbVotes = self.get_element_text((By.XPATH, "//span[@class='sc-7ab21ed2-1 jGRxWM']"))
                # imdbID = self.driver.current_url.split('/')[-2]  # Extract imdbID from the URL
                # boxOffice = self.get_element_text((By.XPATH, "//span[contains(@class, 'ipc-metadata-list-item__list-content-item') and contains(text(), '$')]"))

                # Add scraped data to the movie dictionary
                movie.update({
                    'imdbRating': imdbRating,
                    'Year': year,
                    'Runtime': runtime,
                    'Rated': rated,
                    'Released': released,
                    'Genre': genre,
                    'Director': director,
                    # 'Writer': writer,
                    # 'Actors': actors,
                    # 'Plot': plot,
                    # 'Language': language,
                    # 'Country': country,
                    # 'Awards': awards,
                    # 'Poster': poster,
                    # 'imdbVotes': imdbVotes,
                    # 'imdbID': imdbID,
                    # 'BoxOffice': boxOffice
                })
                
                print(f"Finished: {movie['Title']}")
            
            except Exception as e:
                print(f"Error scraping movie: {movie['Link']}, {str(e)}")
        
        return movie_data
    


    def scroll_slowly(self, step_size=1000, pause_time=0.25):
        """
        Scrolls down the page slowly in increments.
        
        :param step_size: Number of pixels to scroll down per step.
        :param pause_time: Time to pause between each scroll step.
        """
        # Get the initial height of the page
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        current_position = 0
        
        while current_position < last_height:
            # Scroll down by the step size
            self.driver.execute_script(f"window.scrollBy(0, {step_size});")
            
            # Update the current position
            current_position += step_size
            
            # Wait for the page to load new content (if any)
            time.sleep(pause_time)
            
            # Get the updated page height in case new content was loaded
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # If the new content extends the height, update the last height
            if new_height > last_height:
                last_height = new_height

    def clean_movie_title(self, title):
        clean_title = title.split('. ', 1)[-1].strip()
        return clean_title
    
    def wait_for_element(self, locator, timeout=30):
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located(locator))

    def wait_for_elements(self, locator, timeout=30):
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