import os
import time
from script_scraper import MovieScriptScraper
from scrapy.crawler import CrawlerProcess
from data_manipulation import clean_database

def setup_output_directory():
    if not os.path.exists("scripts"):
        os.makedirs("scripts")
        print("Created 'scripts' directory.")

def run_spider():
    process = CrawlerProcess()
    process.crawl(MovieScriptScraper)
    process.start()

def main():
    # setup_output_directory()
    
    print("Starting web scraping...")
    run_spider()
    
    print("Web scraping completed. Cleaning the database...")
    time.sleep(2)  # Give some time for the database to be updated
    clean_database()
    
    print("Process completed successfully.")

if __name__ == "__main__":
    main()