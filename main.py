# main.py (FastAPI App with Upload, Scraping Options, Email, and File Download)

import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app import main as scrape_main
from typing import List
from datetime import datetime

app = FastAPI()

# CORS setup to allow frontend on different origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "./uploads"
SCRAPE_OUTPUT_FOLDER = "./amazon_data"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SCRAPE_OUTPUT_FOLDER, exist_ok=True)

@app.post("/scrape/")
async def scrape_amazon(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    company: str = Form(...),
    pincodes: str = Form(...),  # comma-separated
    sendMailFlag: bool = Form(False),
    getCompetitorFlag: bool = Form(True),
    getProductTitleFlag: bool = Form(True),
):
    file_location = f"{UPLOAD_FOLDER}/{file.filename}"
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # convert to list
    pincodes_list = [code.strip() for code in pincodes.split(",") if code.strip()]

    city_map = {
        "400001": "Mumbai",
        "110001": "Delhi",
        "560001": "Bangalore",
        "500001": "Hyderabad",
        "201301": "Noida",
        "600001": "Chennai",
        "700002": "Kolkata",
        "226001": "Lucknow"
    }

    # rename uploaded file as company.csv
    company_csv_path = f"./{company}.csv"
    shutil.copyfile(file_location, company_csv_path)

    # build output file name
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    output_filename = f"{company}_{timestamp}.csv"

    # run scraping in background
    background_tasks.add_task(
        scrape_main,
        company,
        pincodes_list,
        city_map,
        sendMailFlag,
        getCompetitorFlag,
        getProductTitleFlag
    )

    return {"message": "Scraping started.", "download_url": f"/download/{company}_{timestamp}.csv"}


@app.get("/download/{filename}")
def download_file(filename: str):
    filepath = f"{SCRAPE_OUTPUT_FOLDER}/{filename}"
    if os.path.exists(filepath):
        return FileResponse(path=filepath, media_type='application/octet-stream', filename=filename)
    return {"error": "File not found"}


@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <h2>Amazon Scraper API is Running</h2>
    <p>Use a frontend or Postman to test scraping.</p>
    """
