from scraper import ImdbScraper
from pipeline import MoviePipeline
import time
import logging

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    start_time = time.time()
    
    url = 'https://www.imdb.com/search/title/?title_type=feature&genres=sci-fi&interests=in0000076&sort=num_votes,desc&language=en'
    
    try:
        scraper = ImdbScraper(url, headless=False, num_workers=1, num_titles=5)  # !! max 8 is important to not to hammer website's server
        movie_data = scraper.run_scraper()
        logging.info(f"Scraped {len(movie_data)} movies")
        
        db_pipeline = MoviePipeline()
        db_pipeline.process_movies(movie_data)
        db_pipeline.close()
        
        end_time = time.time()
        run_time = end_time - start_time
        logging.info(f"Runtime: {run_time:.2f} seconds")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()