# Movie Recommender System

## Project Overview
This project is a movie recommendation engine that uses:
- **MySQL** for structured movie data.
- **VLLM (Qwen3-0.6B)** for analyzing user watch history and identifying themes.
- **ChromaDB + Qwen3-Embedding-0.6B** for vector-based movie recommendations.
- **FastAPI** for the backend logic.
- **React + Vite + TailwindCSS** for the frontend UI.

## Deployment Instructions (Ubuntu)

### 1. Prerequisites
Ensure you have `python3.10+`, `npm`, `mysql-server`, and `cuda` drivers (if using GPU) installed.

### 2. Database Setup
Ensure your MySQL database `umd` is running and populated.
Update `backend/database.py` if your credentials differ from the defaults.

### 3. LLM Service (VLLM)
Open a terminal for the LLM service:
```bash
cd llm_server
chmod +x start_llm.sh
./start_llm.sh
```
*This starts the Qwen3-0.6B model on port 8000.*

### 4. Backend Setup
Open a new terminal for the Backend:
```bash
cd backend
pip install -r requirements.txt
```

**Data Ingestion (Run Once):**
Before starting the API, ingest the movie embeddings into ChromaDB:
```bash
python ingest.py
```

**Start API:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```
*The backend API runs on port 8001.*

### 5. Frontend Setup
Open a new terminal for the Frontend:
```bash
cd frontend
npm install
npm run build
npm run preview -- --port 3000
```
Or for development:
```bash
npm run dev
```

## Access
Open your browser and navigate to `http://<your-server-ip>:3000`.

## Architecture Note
- The **Backend** loads the embedding model locally (Qwen3-Embedding) for generating query vectors.
- The **Backend** calls the **VLLM Service** (localhost:8000) for chat completions.
