from scraper import ImdbScraper
from movie_data_api import MovieDataAPI
from pipeline import MoviePipeline
import time

# TODO: right now we hardcode the data into code without any configuration this will change into actual search.
def main():
    start_time = time.time()
    
    url = 'https://www.imdb.com/search/title/?title_type=feature&genres=sci-fi&interests=in0000076&sort=num_votes,desc&language=en'
    
    scraper = ImdbScraper(url, headless=True)
    movie_data = scraper.run_scraper()
    print(movie_data) # for testing
    
    # TODO: will be integrated fully with pipeline
    # omdb_api = MovieDataAPI(titles)
    
    db_pipeline = MoviePipeline()
    db_pipeline.process_movies(movie_data) # omdb_api.get_movie_data()
    db_pipeline.close()
    
    end_time = time.time()
    run_time = end_time - start_time
    print(f"Runtime: {run_time} seconds")

if __name__ == "__main__":
    main()
    