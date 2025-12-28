from openai import OpenAI
import torch
from transformers import AutoModel, AutoTokenizer
import os

# Configuration
VLLM_API_BASE = "http://localhost:8000/v1"
VLLM_API_KEY = "EMPTY" # VLLM usually doesn't need a key locally
EMBEDDING_MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"

_tokenizer = None
_model = None

def get_embedding_model():
    global _tokenizer, _model
    if _model is None:
        print("Loading embedding model...")
        _tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL_NAME, trust_remote_code=True)
        _model = AutoModel.from_pretrained(EMBEDDING_MODEL_NAME, trust_remote_code=True)
        _model.eval()
    return _tokenizer, _model

def generate_query_embedding(text):
    tokenizer, model = get_embedding_model()
    inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt", max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1)
    return embedding[0].cpu().numpy().tolist()

def identify_common_theme(watched_movies):
    """
    Sends watched movies to LLM to find common theme.
    watched_movies: List of dicts (title, plot, etc.)
    """
    client = OpenAI(
        api_key=VLLM_API_KEY,
        base_url=VLLM_API_BASE,
    )

    # Construct prompt
    movies_desc = ""
    for idx, m in enumerate(watched_movies, 1):
        movies_desc += f"{idx}. Title: {m['title']}\n   Plot: {m.get('Plot')}\n   Starring: {m.get('Starring')}\n   Director: {m.get('director_name', 'Unknown')}\n\n"

    system_prompt = (
        "You are a movie expert. Analyze the given list of movies and identify the most prominent common theme, "
        "plotline, actor, or director among them. "
        "Output ONLY a JSON object with the following format:\n"
        "{\"type\": \"plotline/actor/director\", \"detail\": \"Description of the commonality\"}\n"
        "Do not include any other text."
    )

    user_prompt = f"Here are the movies I watched:\n\n{movies_desc}\nFind the common theme."

    try:
        response = client.chat.completions.create(
            model="Qwen/Qwen3-0.6B",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        content = response.choices[0].message.content
        # Depending on model capability, it might output reasoning or just JSON.
        # User asked for reasoning to be shown.
        # Since standard OpenAI api doesn't separate 'thought' unless using specific models/params,
        # we will just return the content. The user said "Show both the result and reasoning thought".
        # We can ask the model to include reasoning in the JSON or separately?
        # Let's ask it to output reasoning in the response text, and we try to parse the JSON out of it.
        return content
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return json.dumps({"type": "error", "detail": str(e), "reasoning": "Failed to contact LLM"})

import json
