import sqlite3

# TODO: these SQL codes will change because some data that will be retrieved from the IMDB will be missing.
class MoviePipeline:
    def __init__(self, db_name="movies.db"):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        # Create a table for movies
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                year TEXT,
                rated TEXT,
                released TEXT,
                runtime TEXT,
                genre TEXT,
                director TEXT,
                writer TEXT,
                actors TEXT,
                plot TEXT,
                language TEXT,
                country TEXT,
                awards TEXT,
                poster TEXT,
                link TEXT,
                imdbRating TEXT,
                imdbVotes TEXT,
                imdbID TEXT,
                boxOffice TEXT
            )
        ''')
        self.connection.commit()

    def insert_movie_data(self, movie_data):
        # Insert the movie data into the database
        self.cursor.execute('''
            INSERT INTO movies (
                title, year, rated, released, runtime, genre, director, writer, actors, plot, language, 
                country, awards, poster, link, imdbRating, imdbVotes, imdbID, boxOffice
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            movie_data.get('Title'),
            movie_data.get('Year'),
            movie_data.get('Rated'),
            movie_data.get('Released'),
            movie_data.get('Runtime'),
            movie_data.get('Genre'),
            movie_data.get('Director'),
            movie_data.get('Writer'),
            movie_data.get('Actors'),
            movie_data.get('Plot'),
            movie_data.get('Language'),
            movie_data.get('Country'),
            movie_data.get('Awards'),
            movie_data.get('Poster'),
            movie_data.get('Link'),
            movie_data.get('imdbRating'),
            movie_data.get('imdbVotes'),
            movie_data.get('imdbID'),
            movie_data.get('BoxOffice')
        ))
        self.connection.commit()

    def process_movies(self, movie_data):
        for movie_data in movie_data:
            self.insert_movie_data(movie_data)

    def close(self):
        self.connection.close()

