import logging
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


# Configure logging
logger = logging.getLogger("server")
logger.setLevel(logging.DEBUG)

app = FastAPI()

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=FileResponse)
async def serve_home():
    """Serves the main frontend HTML page."""
    return FileResponse(os.path.join("static", "index.html"))

