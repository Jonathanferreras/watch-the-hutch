import logging
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.v1.events import events_controller
from app.api.v1.state import state_controller
from app.api.v1.admin import admin_controller
from app.api.v1.webrtc import webrtc_controller
from app.db import init_db

logger = logging.getLogger("server")
logger.setLevel(logging.DEBUG)

v1_prefix = "/api/v1"
app = FastAPI()

@app.on_event("startup")
def on_startup():
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")

app.include_router(events_controller.router, prefix=v1_prefix)
app.include_router(state_controller.router, prefix=v1_prefix)
app.include_router(admin_controller.router, prefix=f"{v1_prefix}/admin")
app.include_router(webrtc_controller.router)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=FileResponse)
async def serve_home():
    return FileResponse(os.path.join("static", "index.html"))

@app.get("/admin", response_class=FileResponse)
async def serve_admin():
    return FileResponse(os.path.join("static", "admin.html"))
