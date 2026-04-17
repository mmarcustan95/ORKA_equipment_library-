import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from typing import List
from main.models import ValidationEntry

app = FastAPI(title="ORKA Equipment Knowledge Library")

# In-memory storage for Stage 1 (will be replaced by SharePoint List in Stage 2)
db: List[ValidationEntry] = []

@app.get("/", tags=["Health"])
async def root():
    return {"message": "ORKA Equipment Knowledge API is running"}

@app.get("/entries", response_model=List[ValidationEntry], tags=["Entries"])
async def get_entries():
    """Retrieve all validation knowledge entries."""
    return db

@app.post("/entries", response_model=ValidationEntry, tags=["Entries"])
async def create_entry(entry: ValidationEntry):
    """Log a new equipment validation lesson learned."""
    db.append(entry)
    return entry

# Optional: Mount static files if you have a 'public' folder for the frontend
if os.path.exists(" main/public"):
    app.mount("/static", StaticFiles(directory="main/public"), name="static")
