import sqlite3
from itemadapter import ItemAdapter
import os

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