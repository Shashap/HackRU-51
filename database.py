import sqlite3
from datetime import datetime, timedelta
from scrape_classes import SearchResult


def create_tables():
    conn = sqlite3.connect("searchdb.db")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS search_query
                      (Query TEXT PRIMARY KEY, Time TIMESTAMP)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS search_results
                      (ASIN TEXT, Name TEXT PRIMARY KEY, Query TEXT, Image TEXT, Rating REAL, Price_Amazon_com REAL, Link_Amazon_com TEXT,
                      Price_Amazon_ca REAL, Link_Amazon_ca TEXT, Price_Amazon_uk REAL, Link_Amazon_uk TEXT,
                      Price_Amazon_de REAL, Link_Amazon_de TEXT, Time TIMESTAMP, FOREIGN KEY(Query) REFERENCES search_query(Query))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS results_history
                      (ASIN TEXT, Name TEXT, Query TEXT, Image TEXT, Rating REAL, Price_Amazon_com REAL, Link_Amazon_com TEXT,
                      Price_Amazon_ca REAL, Link_Amazon_ca TEXT, Price_Amazon_uk REAL, Link_Amazon_uk TEXT,
                      Price_Amazon_de REAL, Link_Amazon_de TEXT, Time TIMESTAMP, PRIMARY KEY(Query, Time),
                      FOREIGN KEY(Query) REFERENCES search_query(Query), FOREIGN KEY(Name) REFERENCES search_results(Name))''')

    conn.commit()
    conn.close()


def delete_all_search_results():
    conn = sqlite3.connect("searchdb.db")
    cursor = conn.cursor()
    cursor.execute('DELETE FROM search_results')
    conn.commit()
    conn.close()


def clear_search_tables():
    conn = sqlite3.connect("searchdb.db")
    cursor = conn.cursor()
    cursor.execute('DELETE FROM search_results')
    cursor.execute('DELETE FROM search_query')
    conn.commit()
    conn.close()


def check_10_rows(last_24_hours=False):
    conn = sqlite3.connect("searchdb.db")
    cursor = conn.cursor()
    if last_24_hours:
        yesterday = datetime.now() - timedelta(days=1)
        cursor.execute("SELECT COUNT(*) FROM results_history WHERE Time > ?", (yesterday,))
    else:
        cursor.execute(f"SELECT COUNT(*) FROM search_results")
    count = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return count >= 10


def insert_item_search_results(query, name, link, price, image, rating, asin):
    conn = sqlite3.connect("searchdb.db")
    cursor = conn.cursor()
    cursor.execute("SELECT Time FROM search_query WHERE Query=?", (query,))
    time = cursor.fetchone()[0]
    cursor.execute(
        "INSERT OR IGNORE INTO search_results (ASIN, Name, Query, Image, Rating, Price_Amazon_com, Link_Amazon_com, Time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (asin, name, query, image, rating, price, link, time))
    conn.commit()
    conn.close()


def update_item_search_results(name, identifier, price, link):
    conn = sqlite3.connect("searchdb.db")
    cursor = conn.cursor()
    cursor.execute(
        f'UPDATE search_results SET Price_Amazon_{identifier} = ?, Link_Amazon_{identifier} = ? WHERE Name = ?',
        (price, link, name))
    conn.commit()
    conn.close()


def get_row_by_pk_search_results(name):
    conn = sqlite3.connect("searchdb.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM search_results WHERE Name=?", (name,))
    row = cursor.fetchone()
    if row is None:
        return None
    search_result = SearchResult(**{k: row[i] for i, k in enumerate(SearchResult.__fields__.keys())})
    return search_result


def get_search_results(query):
    conn = sqlite3.connect("searchdb.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM search_results WHERE Query=?", (query,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_results_history():
    conn = sqlite3.connect("searchdb.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM results_history")
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_results_history(name):
    search_result = get_row_by_pk_search_results(name)
    conn = sqlite3.connect("searchdb.db")
    cursor = conn.cursor()
    cursor.execute('''INSERT OR IGNORE INTO results_history
                          (ASIN, Name, Query, Image, Rating, Price_Amazon_com, Link_Amazon_com,
                          Price_Amazon_ca, Link_Amazon_ca, Price_Amazon_uk, Link_Amazon_uk,
                          Price_Amazon_de, Link_Amazon_de, Time)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (*search_result.dict().values(),))

    conn.commit()
    conn.close()
    query = search_result.Query
    return query


def insert_new_query(query, time):
    conn = sqlite3.connect("searchdb.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO search_query (Query, Time) VALUES (?, ?)", (query, time))
    conn.commit()
    conn.close()

