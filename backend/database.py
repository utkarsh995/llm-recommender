import mysql.connector
import chromadb
from chromadb.config import Settings
import os
import json

# MySQL Configuration
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_DATABASE = "umd"
DB_USER = "umd"
DB_PASSWORD = "umd1234"

# ChromaDB Configuration
CHROMA_PATH = "../chroma_db"

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_DATABASE,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

def get_chroma_client():
    return chromadb.PersistentClient(path=CHROMA_PATH)

def fetch_movie_details(title_list):
    """Fetches details for a list of movie titles."""
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    format_strings = ','.join(['%s'] * len(title_list))
    query = f"SELECT * FROM content_details WHERE title IN ({format_strings})"
    
    try:
        cursor.execute(query, tuple(title_list))
        rows = cursor.fetchall()
        
        # Parse JSON fields
        for row in rows:
            if isinstance(row['Starring'], str):
                try:
                    row['Starring'] = json.loads(row['Starring'])
                except:
                    pass # Keep as string if parsing fails
            if isinstance(row['principalCrewMembers'], str):
                try:
                    row['principalCrewMembers'] = json.loads(row['principalCrewMembers'])
                except:
                    pass
        return rows
    finally:
        cursor.close()
        conn.close()

def search_movies_wildcard(query_str):
    """Searches movies with wildcard matching."""
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT program_id, title, year, image_url FROM content_details WHERE title LIKE %s LIMIT 20"
    
    try:
        cursor.execute(sql, (f"%{query_str}%",))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
