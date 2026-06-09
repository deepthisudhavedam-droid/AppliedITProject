import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from routers import analyze, outfits

from fastapi.middleware.cors import CORSMiddleware 
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#THE CORS middleware is used to connect the frontend ports and backend poerts.
# as my frontend uses port 5173 and backend uses port 8000, without this middleware,
# the frontend will not be able to communicate with the backend due to CORS policy.  

app.include_router(analyze.router)
app.include_router(outfits.router)


@app.get("/health")
def health():
    return {"status": "ok"}

