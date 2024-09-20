# IMDB Movie Data Scraper, Database and Analysis

## Project Overview

This project is a comprehensive IMDB movie data scraper that extracts detailed information about movies and stores it in a SQLite database. The primary goal is to create a custom dataset for personal data analysis projects while focusing on learning and implementing web scraping techniques.

The sole usage of this project is for educational purposes. The data is freely available on the IMDB website, and the project follows the rules outlined in the site's `robots.txt`. This scraper adheres to respectful scraping practices by introducing delays between requests only fetching the necessary data and also small scope of movies are scraped for the analysis objective, ensuring compliance with the site's rate limits and terms of use.

## Purpose and Objectives

The primary objectives of this project are:

1. To learn and apply advanced web scraping techniques in a real-world scenario.
2. To build a custom, up-to-date movie database directly from IMDB, without relying on external datasets.
3. To gather and prepare data for analysis purposes.
4. To experience the challenges of working with real-world web data and develop effective solutions for managing and processing it.

## Components

The project consists of three main Python scripts:

1. **scraper.py**: Contains the `ImdbScraper` class responsible for web scraping.
2. **pipeline.py**: Houses the `MoviePipeline` class that handles data processing and database operations.
3. **main.py**: Orchestrates the entire scraping and data storage process.

## Technologies and Libraries Used

- **Python**: The primary programming language used.
- **SQL**: The most necessary part for the pipeline.
- **Selenium**: For web scraping and browser automation.
- **concurrent.futures**: To implement multi-threading for faster scraping.
- **sqlite3**: For creating and managing the SQLite database.

## Key Features

### Multi-threaded Scraping

The `ImdbScraper` class utilizes Python's `concurrent.futures` module to implement multi-threading. This significantly speeds up the scraping process by allowing multiple pages to be scraped simultaneously.

```python
with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
    future_to_movie = {executor.submit(self.scrape_single_movie, title, link): (title, link) for title, link in zip(movie_titles, movie_links)}
```

### Efficient Data Storage

The `MoviePipeline` class manages data storage, using SQLite for its simplicity and efficiency. It handles data insertion and manages potential duplicates.

```python
def insert_movie_data(self, movie_data):
    try:
        self.cursor.execute('''
            INSERT OR REPLACE INTO movies (
                title, year, rated, released, runtime, genre, director, writer, actors, plot, language,
                country, poster, imdbRating, imdbVotes, imdbID, boxOfficeBudget, boxOfficeGross
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (...))
        self.connection.commit()
    except sqlite3.IntegrityError:
        logging.warning(f"Duplicate entry for imdbID: {movie_data.get('imdbID')}")
```

## Data Collected

The scraper collects comprehensive information about each movie, including:

- Title, Year, Runtime, Genre
- IMDB Rating and Votes
- Director, Writer and Actors
- Plot summary
- Language and Country
- Poster URL
- Box Office Budget and Gross

## Future: Data Analysis

The next phase of this project will focus on analyzing the collected data. Potential areas of analysis include:

- Trend analysis of movie ratings over different decades
- Correlation studies between budget, box office performance, and ratings
- Genre popularity shifts over time
- Network analysis of collaborations between directors, writers, and actors
- Predictive modeling for movie success based on various factors

## Installation and Usage

**1.** Clone the repository:

**2.** Install required dependencies:

```python
pip install selenium
```

**3.** Ensure Chrome and ChromeDriver are installed and properly configured

**4.** Use a link from specific search filters from the example website:

- https://www.imdb.com/search/title/?title_type=feature&genres=sci-fi&interests=in0000076&sort=num_votes,desc&language=en

**5.** Then paste this link to url section in `main.py` the script currently work on this specific link and pulls up to 50 movies from the filtered movies. A method for additional movie scrape will be added.

```python
url = 'https://www.imdb.com/search/title/?title_type=feature&genres=sci-fi&interests=in0000076&sort=num_votes,desc&language=en'
```

**6.** Run the main script then the scrape process will begin.

**7.** `movies.db` will be created on the working folder. This SQLite file is designated for the usecase in projects in local environment. To view the file python scripts can be initialized, [DB Browser](https://sqlitebrowser.org/) can be used if installed or the web apps like [sqliteviewer](https://sqliteviewer.app/) can be used for fast examination.

## Disclaimer

This project is intended for educational and personal use only. It was developed to explore web scraping techniques and create a custom movie database for learning purposes. The data is sourced from publicly available information on IMDB, and all scraping activities follow ethical guidelines, including rate-limiting and compliance with the site's terms of service.

Please ensure that you respect IMDB’s terms of use and avoid using the project for any commercial or unauthorized purposes.
