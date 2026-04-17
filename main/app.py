import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from typing import List
from main.models import ValidationEntry
from main.local_db import test_db

from fastapi.responses import FileResponse

app = FastAPI(title="ORKA Equipment Knowledge Library")

@app.get("/")
async def root():
    """Serve the frontend dashboard."""
    return FileResponse("main/public/index.html")

@app.get("/entries", response_model=List[ValidationEntry], tags=["Entries"])
async def get_entries():
    """Retrieve all validation knowledge entries from the LOCAL TEST database."""
    try:
        return test_db.get_entries()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/entries", response_model=ValidationEntry, tags=["Entries"])
async def create_entry(entry: ValidationEntry):
    """Log a new equipment validation lesson learned to the LOCAL TEST database."""
    try:
        return test_db.create_entry(entry)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Optional: Mount static files
if os.path.exists("main/public"):
    app.mount("/static", StaticFiles(directory="main/public"), name="static")
