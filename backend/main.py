from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Any
from pydantic import BaseModel
import json
import re

from database import search_movies_wildcard, fetch_movie_details, get_chroma_client
from llm_service import identify_common_theme, generate_query_embedding

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Movie(BaseModel):
    program_id: int
    title: str
    year: Optional[int] = None
    image_url: Optional[str] = None
    Plot: Optional[str] = None
    Starring: Optional[Any] = None # Can be list or string depending on parsing
    principalCrewMembers: Optional[Any] = None

class WatchHistory(BaseModel):
    movies: List[Movie]

class ThemeRequest(BaseModel):
    history: List[Movie]

class RecommendationRequest(BaseModel):
    theme_detail: str

@app.get("/search")
def search_movies(q: str):
    results = search_movies_wildcard(q)
    return results

@app.post("/identify_theme")
def get_theme(request: ThemeRequest):
    # We might need more details than what's in the minimal search result
    # Fetch full details for the movies in history to pass to LLM
    movie_ids = [m.title for m in request.history] # Using title for fetch based on db helper
    # Actually db helper 'fetch_movie_details' takes title list.
    full_details = fetch_movie_details([m.title for m in request.history])
    
    # Process for LLM
    # Helper to clean/prepare data
    processed_movies = []
    for m in full_details:
        # Extract director
        director = "Unknown"
        crew = m.get('principalCrewMembers', [])
        if isinstance(crew, list):
            for member in crew:
                if isinstance(member, dict) and member.get('category') == 'director':
                    director = member.get('nameId', '') or member.get('imdbName', '')
                    break
        processed_movies.append({
            "title": m['title'],
            "Plot": m['Plot'],
            "Starring": m['Starring'],
            "director_name": director
        })

    raw_response = identify_common_theme(processed_movies)
    
    # Attempt to parse specific JSON pattern if mixed with text
    # expected: ... JSON: {...} or just {...}
    json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
    parsed_json = {}
    reasoning = raw_response
    
    if json_match:
        try:
            parsed_json = json.loads(json_match.group(0))
        except:
            pass
            
    return {
        "raw_output": raw_response,
        "parsed_theme": parsed_json,
        "reasoning": reasoning # In a real implementation we'd separate them better
    }

@app.post("/recommend")
def get_recommendations(request: RecommendationRequest):
    query_text = request.theme_detail
    print(f"Generating embedding for: {query_text}")
    embedding = generate_query_embedding(query_text)
    
    client = get_chroma_client()
    collection = client.get_collection(name="movie_embeddings")
    
    results = collection.query(
        query_embeddings=[embedding],
        n_results=10
    )
    
    # Transform results
    recommendations = []
    if results['ids']:
        metadatas = results['metadatas'][0]
        ids = results['ids'][0]
        for i, meta in enumerate(metadatas):
            recommendations.append({
                "program_id": ids[i], # using ID as string
                "title": meta['title'],
                "year": meta['year'],
                "image_url": meta['image_url']
            })
            
    return recommendations

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
