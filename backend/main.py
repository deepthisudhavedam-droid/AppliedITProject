import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from routers import analyze, outfits, auth
from database.connection import init_db

from fastapi.middleware.cors import CORSMiddleware 
app = FastAPI()

logger = logging.getLogger("uvicorn.error")

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception while processing request %s %s", request.method, request.url, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Check backend logs."},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# The CORS middleware allows the frontend to call this API from a different origin.

app.include_router(auth.router)
app.include_router(analyze.router)
app.include_router(outfits.router)

app.mount("/frontend", StaticFiles(directory="../frontend", html=True), name="frontend")

@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}

