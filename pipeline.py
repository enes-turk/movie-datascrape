import sqlite3
import logging

class MoviePipeline:
    def __init__(self, db_name="movies.db"):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                year INTEGER,
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
                poster TEXT,
                imdbRating TEXT,
                imdbVotes TEXT,
                imdbID TEXT,
                boxOfficeBudget INTEGER,
                boxOfficeGross INTEGER
            )
        ''')
        self.connection.commit()

    def insert_movie_data(self, movie_data):
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO movies (
                    title, year, rated, released, runtime, genre, director, writer, actors, plot, language, 
                    country, poster, imdbRating, imdbVotes, imdbID, boxOfficeBudget, boxOfficeGross
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                movie_data.get('Title'),
                int(movie_data.get('Year')),  # Handle potential year ranges
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
                movie_data.get('Poster'),
                movie_data.get('imdbRating'),
                movie_data.get('imdbVotes'),
                movie_data.get('imdbID'),
                int(movie_data.get('BoxOfficeBudget').replace('$', '').replace(' (estimated)', '').replace(',', '')),
                int(movie_data.get('BoxOfficeGross').replace('$', '').replace(',', ''))
            ))
            self.connection.commit()
        except sqlite3.IntegrityError:
            logging.warning(f"Duplicate entry for imdbID: {movie_data.get('imdbID')}")
        except Exception as e:
            logging.error(f"Error inserting movie data: {str(e)}")

    def process_movies(self, movie_data_list):
        for movie_data in movie_data_list:
            self.insert_movie_data(movie_data)

    def close(self):
        self.connection.close()