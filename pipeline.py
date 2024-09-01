import sqlite3
from itemadapter import ItemAdapter
import os
import sqlite3

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
                country, awards, poster, imdbRating, imdbVotes, imdbID, boxOffice
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

class SQLitePipeline:
    def __init__(self):
        self.conn = None
        self.cur = None

    def open_spider(self, spider):
        self.conn = sqlite3.connect('movie_scripts.db')
        self.cur = self.conn.cursor()
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS scripts
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             title TEXT UNIQUE,
             script TEXT)
        ''')
        self.conn.commit()

    def close_spider(self, spider):
        if self.conn:
            self.conn.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        title = adapter.get('title')
        script = adapter.get('script')

        if title and script:
            try:
                self.cur.execute(
                    'INSERT OR REPLACE INTO scripts (title, script) VALUES (?, ?)',
                    (title, script)
                )
                self.conn.commit()
            except sqlite3.Error as e:
                spider.logger.error(f"SQLite error: {e}")
        else:
            spider.logger.warning(f"Missing title or script for item: {item}")

        return item

class TxtExporter:
    def __init__(self):
        self._setup_output_directory()
    
    def _setup_output_directory(self):
        if not os.path.exists("scripts"):
            os.mkdirs("scripts")
            self.logger.info("Created 'scripts' directory.")
    
    def save_as_txt(self, title, script):
        filename = self._sanitize_filename(title)
        filepath = os.path.join("scripts", filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Title: {title}\n\n")
                f.write(script)
            self.logger.info(f"Saved file: {filename}")
        except IOError as e:
            self.logger.error(f"Error saving file: {filename}: {e}")
    
    @staticmethod
    def _sanitize_filename(filename):
        sanitized = "".join(x for x in filename if x.isalnum() or x in [' ', '_']).rstrip()
        return sanitized.replace(' ', '_') + '.txt'