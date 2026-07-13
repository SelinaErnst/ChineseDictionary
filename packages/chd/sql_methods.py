import sqlite3

def open_db(file):
    conn = sqlite3.connect(file)
    conn.row_factory = sqlite3.Row  
    cursor = conn.cursor()
    return conn, cursor

def close_db(conn):
    conn.commit()
    conn.close()

def table_exists(cursor, name:str):
    cursor.execute('''
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
    ''', (name,))
    return cursor.fetchone() is not None

def get_table_names(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    return tables

def remove_table(cursor,name:str):
    cursor.execute(f"DROP TABLE IF EXISTS {name}")

def create_table(cursor,name:str,columns:list):
    cols = ", ".join(columns)
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {name} ({cols})")
    placeholders = ", ".join(["?" for _ in columns])
    insert_query = f"INSERT INTO {name} VALUES ({placeholders})"
    return insert_query