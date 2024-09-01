from scraper import ImdbTitlesScraper
from movie_data_api import MovieDataAPI
from pipeline import MoviePipeline

def main():
    url = 'https://www.imdb.com/search/title/?title_type=feature&genres=sci-fi&interests=in0000076&sort=num_votes,desc&language=en'
    
    title_scraper = ImdbTitlesScraper(url)
    titles = title_scraper.run_scraper()
    
    omdb_api = MovieDataAPI(titles)
    
    db_pipeline = MoviePipeline()
    db_pipeline.process_movies(omdb_api.get_movie_data())
    db_pipeline.close()

if __name__ == "__main__":
    main()
    
    