import sqlite3
import re

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
    add_columns(cursor,name,columns)
    placeholders = ", ".join(["?" for _ in columns])
    columns = [re.findall(r'"([^"]*)"', item)[0] for item in columns]
    cols = ", ".join(columns)
    insert_query = f"INSERT INTO {name} ({cols}) VALUES ({placeholders})"
    return insert_query

def get_table_columns(cursor,name:str):
    cursor.execute(f"SELECT * FROM {name} LIMIT 0")
    column_names = [description[0] for description in cursor.description]
    return column_names

def get_column_type(dtype):
    dtype_map = {
        str:'TEXT',
        int:'INTEGER',
        float:'NUMERIC',
        list:'TEXT',
        dict:'TEXT',
    }
    if dtype not in dtype_map.keys(): return 'TEXT'
    else: return [t for d,t in dtype_map.items() if dtype==d][0]
    
def create_column_list(columns:dict):
    return [f'"{k}" {get_column_type(v)}' for k,v in columns.items()]
    
def add_columns(cursor,name:str,new_columns:dict):
    old_columns = get_table_columns(cursor,name)
    if isinstance(new_columns,dict):
        new_columns = {k:v for k,v in new_columns.items() if k not in old_columns}
        new_columns = create_column_list(new_columns)
    elif isinstance(new_columns,list):
        new_columns = [col for col in new_columns if not any([old in col for old in old_columns])]
    for col in new_columns:
        cursor.execute(f"ALTER TABLE {name} ADD COLUMN {col}")
        
        
def get_unique_values(cursor,name,column:str):
    cursor.execute(f"SELECT DISTINCT {column} FROM {name}")
    unique_values = [row[0] for row in cursor.fetchall()]
    return unique_values