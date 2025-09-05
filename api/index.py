from fastapi import FastAPI
from fastapi.responses import Response
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World from Vercel!"}

@app.get("/test")
def test():
    return {"message": "Test endpoint works!", "working_dir": os.getcwd()}

@app.get("/health")
def health():
    return {"status": "healthy"}

# Export for Vercel
handler = app