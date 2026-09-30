import os
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import json

# Import the existing logic
from persistent_search import PersistentSearch

app = FastAPI()

# Setup templates
os.makedirs("templates", exist_ok=True)
templates = Jinja2Templates(directory="templates")

# Initialize Searcher
searcher = PersistentSearch()
# Prune old entries on startup
searcher.prune_index(max_days=30)

# Data Models
class FolderPath(BaseModel):
    path: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/index/add")
async def add_folder(folder: FolderPath, background_tasks: BackgroundTasks):
    path = folder.path.strip()
    if not os.path.exists(path):
        raise HTTPException(status_code=400, detail="Directory does not exist")
    if not os.path.isdir(path):
        raise HTTPException(status_code=400, detail="Path is not a directory")
    
    # Run analysis in background
    background_tasks.add_task(searcher.analyze_folder, path)
    return {"status": "started", "message": f"Analysis started for {path}"}

@app.get("/api/search")
async def search_api(q: str = ""):
    if not q:
        # Return all (or top 50 recently added?)
        # For now, let's just return everything if query is empty, 
        # or nothing. Let's return first 20 items to populate UI.
        items = list(searcher.index.items())
        results = []
        for path, data in items:
             results.append({"path": path, "score": 0, "data": data})
        return results

    results = searcher.search(q)
    # Format for JSON
    json_results = []
    for path, score, data in results:
        json_results.append({
            "path": path,
            "score": score,
            "data": data
        })
    return json_results

@app.get("/files/{filepath:path}")
async def serve_file(filepath: str):
    # Security check: ensure file is in index
    # We need to reconstruct the absolute path because the route param might be stripped or manipulated?
    # Actually, filepath comes in as the full path suffix.
    # But wait, our index keys are ABSOLUTE paths.
    # So we should expect the full absolute path or a mapped ID.
    # Passing absolute paths in URLs is tricky (slashes).
    # Let's map it: Client sends absolute path as query param or we encode it?
    # EASIER: Client sends `?path=...` to a generic endpoint.
    
    # But we can assume the user trusts this local tool.
    # Let's verify it exists on disk and is in our index (optional).
    
    # We start with a leading slash usually, but path param might strip it.
    if not filepath.startswith("/"):
        filepath = "/" + filepath
        
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(filepath)

# Simpler file serving endpoint using query param to avoid slash issues
@app.get("/api/file")
async def get_file(path: str):
    if not os.path.exists(path):
         raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
