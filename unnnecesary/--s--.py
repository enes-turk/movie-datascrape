import os
import time
import logging
from urllib.parse import urljoin

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import DropItem

class MovieScriptScraper(scrapy.Spider):
    """
    A Scrapy spider for scraping movie scripts from subslikescript.com.
    
    This spider crawls the website, extracts movie scripts, and saves them as text files.
    It implements rate limiting and error handling to respect the website's resources.
    """

    name = 'movie_script_scraper'
    
    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'RETRY_TIMES': 5,
        'RETRY_HTTP_CODES': [429, 500, 502, 503, 504, 522, 524, 408, 400],
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'LOG_LEVEL': 'INFO',
    }

    def __init__(self, *args, **kwargs):
        """
        Initialize the spider with the root URL and create the output directory.
        """
        super(MovieScriptScraper, self).__init__(*args, **kwargs)
        self.root = 'https://subslikescript.com'
        self.start_urls = ['https://subslikescript.com/movies_letter-X']
        self._setup_output_directory()

    def _setup_output_directory(self):
        """
        Create the 'scripts' directory if it doesn't exist.
        """
        if not os.path.exists("scripts"):
            os.makedirs("scripts")
            self.logger.info("Created 'scripts' directory.")

    def parse(self, response):
        """
        Parse the movie list page, follow links to individual movies, and handle pagination.

        Args:
            response (scrapy.http.Response): The response object for the current page.

        Yields:
            scrapy.Request: Requests for individual movie pages and the next page of movie listings.
        """
        # Extract and follow links to individual movie pages
        movie_links = response.xpath("//article[@class='main-article']/ul/li/a/@href").getall()
        for link in movie_links:
            yield scrapy.Request(
                url=urljoin(self.root, link),
                callback=self.parse_movie,
                dont_filter=True
            )

        # Handle pagination
        next_page = response.xpath("//a[@rel='next']/@href").get()
        if next_page:
            next_page_url = urljoin(response.url, next_page)
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse,
                dont_filter=True
            )

    def parse_movie(self, response):
        """
        Parse individual movie pages to extract the script.

        Args:
            response (scrapy.http.Response): The response object for the movie page.

        Yields:
            scrapy.Request: A new request if a 429 status is encountered.
        """
        if response.status == 429:
            self.logger.warning(f"Received 429 response. Retrying after delay: {response.url}")
            time.sleep(60)  # Wait for 60 seconds before retrying
            yield scrapy.Request(
                url=response.url,
                callback=self.parse_movie,
                dont_filter=True
            )
            return

        title = response.xpath("//article[@class='main-article']/h1/text()").get()
        script = response.xpath("//article[@class='main-article']/div[@class='full-script']/text()").getall()
        script = ' '.join(script).strip()

        if not title or not script:
            raise DropItem(f"Missing title or script in {response.url}")

        self.save_as_txt(title, script)

    def save_as_txt(self, title, script):
        """
        Save the movie script as a text file.

        Args:
            title (str): The title of the movie.
            script (str): The full text of the movie script.
        """
        filename = self._sanitize_filename(title)
        filepath = os.path.join("scripts", filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Title: {title}\n\n")
                f.write(script)
            self.logger.info(f"Saved file: {filename}")
        except IOError as e:
            self.logger.error(f"Error saving file {filename}: {e}")

    @staticmethod
    def _sanitize_filename(filename):
        """
        Sanitize the filename to ensure it's valid for the file system.

        Args:
            filename (str): The original filename.

        Returns:
            str: A sanitized version of the filename.
        """
        sanitized = "".join(x for x in filename if x.isalnum() or x in [' ', '_']).rstrip()
        return sanitized.replace(' ', '_') + '.txt'

def run_spider():
    """
    Set up and run the Scrapy crawler process.
    """
    process = CrawlerProcess()
    process.crawl(MovieScriptScraper)
    process.start()

if __name__ == "__main__":
    run_spider()