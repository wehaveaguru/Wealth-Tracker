import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys

# Add ui/ directory to path so we can import routes.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ui"))
from ui.routes import app

# Mount the UI folder to serve static HTML files
ui_dir = os.path.join(os.path.dirname(__file__), "ui")
assets_dir = os.path.join(os.path.dirname(__file__), "assets")

# Mount assets if the directory exists
if os.path.isdir(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


# Serve HTML pages from the ui/ folder
@app.get("/")
async def serve_homepage():
    return FileResponse(os.path.join(ui_dir, "homepage.html"))


@app.get("/{page_name}.html")
async def serve_page(page_name: str):
    file_path = os.path.join(ui_dir, f"{page_name}.html")
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(ui_dir, "homepage.html"))


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
