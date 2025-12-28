import os
import json
import torch
import chromadb
from database import get_db_connection, get_chroma_client
from transformers import AutoModel, AutoTokenizer
from tqdm import tqdm

MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"
BATCH_SIZE = 32

def get_text_representation(movie):
    """Creates a text representation of the movie for embedding."""
    title = movie.get('title', '')
    plot = movie.get('Plot', '')
    starring = movie.get('Starring', [])
    if isinstance(starring, list):
        starring = ", ".join(starring)
    elif not isinstance(starring, str):
        starring = ""
        
    director = ""
    crew = movie.get('principalCrewMembers', [])
    if isinstance(crew, list):
        for member in crew:
            if isinstance(member, dict) and member.get('category') == 'director':
                director = member.get('nameId', '') # or imdbName if available? prompting says imdbName in schema
                break
    
    # Combine relevant fields
    text = f"Title: {title}. Plot: {plot}. Starring: {starring}. Director: {director}"
    return text

def generate_embeddings(texts, model, tokenizer):
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt", max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        # Use last hidden state's mean or specific pooling depending on model
        # For typical embedding models, mean pooling is common.
        # Check model card for Qwen3-Embedding if possible, but standard is mean pooling.
        embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings.cpu().numpy().tolist()

def ingest_data():
    print("Connecting to MySQL...")
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to MySQL")
        return

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM content_details")
    movies = cursor.fetchall()
    cursor.close()
    conn.close()
    
    print(f"Fetched {len(movies)} movies.")
    
    print("Loading Model...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    model = AutoModel.from_pretrained(MODEL_NAME, trust_remote_code=True)
    model.eval()

    print("Initializing ChromaDB...")
    client = get_chroma_client()
    collection = client.get_or_create_collection(name="movie_embeddings")

    # Process in batches
    for i in tqdm(range(0, len(movies), BATCH_SIZE)):
        batch_movies = movies[i : i + BATCH_SIZE]
        batch_texts = []
        batch_ids = []
        batch_metadatas = []
        
        for movie in batch_movies:
            # Parse JSON fields if they came as strings (db helper might strictly return strings if not using fetch_movie_details)
            # but here we did raw fetch. Let's ensure parsing.
            if isinstance(movie['Starring'], str):
                try: movie['Starring'] = json.loads(movie['Starring'])
                except: pass
            if isinstance(movie['principalCrewMembers'], str):
                try: movie['principalCrewMembers'] = json.loads(movie['principalCrewMembers'])
                except: pass

            text = get_text_representation(movie)
            batch_texts.append(text)
            batch_ids.append(str(movie['program_id']))
            batch_metadatas.append({
                "title": movie['title'],
                "year": movie['year'],
                "image_url": movie['image_url'] or ""
            })
            
        if batch_texts:
            embeddings = generate_embeddings(batch_texts, model, tokenizer)
            collection.upsert(
                ids=batch_ids,
                embeddings=embeddings,
                metadatas=batch_metadatas,
                documents=batch_texts
            )
            
    print("Ingestion complete.")

if __name__ == "__main__":
    ingest_data()
