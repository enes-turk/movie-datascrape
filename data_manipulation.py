import sqlite3
import re

def create_year_from_title(title):
    pass

def clean_script(script, title):
    # Remove the specific text from the beginning of the script
    cleaned_title = re.sub(r' - full transcript', '', title, flags=re.IGNORECASE)
    cleaned_script = re.sub(r'^foodval\.com - stop by if you\'re interested in the nutritional composition of food\s*---\s*', '', script, flags=re.IGNORECASE)
    return cleaned_script.strip(), cleaned_title.strip()

def clean_database(db_path='movie_scripts.db'):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Fetch all rows
    cur.execute('SELECT id, title, script FROM scripts')
    rows = cur.fetchall()

    # Clean and update each row
    for row in rows:
        id, title, script = row
        cleaned_script, cleaned_title = clean_script(script, title)
        
        cur.execute('UPDATE scripts SET script = ?, title = ? WHERE id = ?', (cleaned_script, cleaned_title, id))
        
        print(f"Cleaned script ID: {id}")

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print("Database cleaning completed.")