from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from urllib.parse import urljoin
import scrapy
from scrapy.exceptions import DropItem
     
class ImdbTitlesScraper:
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
        self.driver = webdriver.Chrome(options=self.options)

    def navigate_to_page(self):
        self.driver.get(self.url)

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
            
            # Wait for the movie titles
            movie_elements = self.wait_for_elements((By.XPATH, "//div[contains(@class, 'ipc-title')]/a/h3"))

            # Scrape titles
            movie_titles = [self.clean_movie_title(element.text) for element in movie_elements[:num_titles]]
            return movie_titles

        except TimeoutException as e:
            print(f"Timeout occurred: {e}")
            print(self.driver.page_source)
            return []

    def close_driver(self):
        if self.driver:
            self.driver.quit()

    def run_scraper(self):
        try:
            self.setup_driver()
            self.navigate_to_page()
            titles = self.scrape_movie_titles()
            # for i, title in enumerate(titles, 1):
            #     print(f"{i}. {title}")
            return titles
        finally:
            self.close_driver()

class MovieScriptScraper(scrapy.Spider):
    name = 'movie_script_scraper'
    
    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN':1,
        'RETRY_TIMES': 5,
        'RETRY_HTTP_CODES': [429, 500, 502, 503, 504, 522, 524, 408, 400],
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'LOG_LEVEL': 'INFO',
        'ITEM_PIPELINES': {
            'pipeline.SQLitePipeline': 300
        }
    }
    
    def __init__(self, *args, **kwargs):
        super(MovieScriptScraper, self).__init__(*args, **kwargs)
        self.root = 'https://subslikescript.com'
        self.start_urls = ['https://subslikescript.com/movies_letter-X']
    
    def parse(self, response):
        movie_links = response.xpath("//article[@class='main-article']/ul/li/a/@href").getall()
        for link in movie_links:
            yield scrapy.Request(
                url=urljoin(self.root, link),
                callback=self.parse_movie,
                dont_filter=True
            )
        
        next_page = response.xpath("//a[@rel='next']/@href").get()
        if next_page:
            next_page_url = urljoin(response.url, next_page)
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse,
                dont_filter=True
            )
    
    def parse_movie(self, response):
        if response.status == 429:
            self.logger.warning(f"Received 429. Retrying after delay: {response.url}")
            time.sleep(10)
            yield scrapy.Request(
                url=response.url,
                callback=self.parse_movie,
                dont_filter=True
            )
            
        title = response.xpath("//article[@class='main-article']/h1/text()").get()
        script = response.xpath("//article[@class='main-article']/div[@class='full-script']/text()").getall()
        script = ' '.join(script).strip()
        
        if not title or not script:
            self.logger.warning(f"Missing title or script in {response.url}")
            raise DropItem(f"Missing title or script in {response.url}")
        
        self.logger.info(f"Processed movie: {title}")
        
        yield {
            'title': title,
            'script': script
        }