from scraper import IMDbScraper

url = 'https://www.imdb.com/search/title/?title_type=feature&genres=sci-fi&interests=in0000076&sort=num_votes,desc&language=en'
scraper = IMDbScraper(url)
scraper.run_scraper()