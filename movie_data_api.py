import requests
from scraper import ImdbTitlesScraper

class MovieDataAPI():
    def __init__(self, movie_titles):
        self.base_url = 'https://www.omdbapi.com/'
        self.api_key = self.read_api_key()
        self.movies = movie_titles  # List of movie titles
        
    # Function to read the API key from cfg.txt
    def read_api_key(self, filename='cfg.txt'):
        with open(filename, 'r') as file:
            for line in file:
                # Split the line into key-value pairs
                key, value = line.strip().split('=')
                if key == 'apikey':
                    return value
        return None

    def get_movie_data(self):
        # Loop through the list of movies
        for movie in self.movies:
            # Parameters for the API request
            params = {
                'apikey': self.api_key,
                't': movie,
                'plot': 'full'
            }
            # Send the request
            response = requests.get(self.base_url, params=params)
            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()
                print(f"Movie: {movie}")
            else:
                print(f"Error fetching data for {movie}: {response.status_code}")
            yield data
