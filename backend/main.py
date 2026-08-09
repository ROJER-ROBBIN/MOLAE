from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.api import chat, search
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Chitraguptar Digital Memory - Phase 2")

# Include API routes
app.include_router(chat.router, prefix="/api/chat")
app.include_router(search.router, prefix="/api/search")

# Mount static frontend files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# Ensure static files can be served (CSS/JS)
app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
