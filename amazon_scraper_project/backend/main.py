# main.py

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import app

scrape_main = app.main


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

class ScrapeRequest(BaseModel):
    company: Optional[str] = "unknown"
    pincodes: Optional[List[str]] = []
    asins: Optional[List[str]] = []
    sendMailFlag: bool = False
    recipient_email: Optional[EmailStr] = None
    getCompetitorFlag: bool = True
    getProductTitleFlag: bool = True
    includePrice: bool = True
    includeSellerCount: bool = True

@app.get("/")
def root():
    return {"message": "Amazon Scraper API is running"}

@app.post("/scrape/")
def scrape_amazon(request: ScrapeRequest, background_tasks: BackgroundTasks):
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

    background_tasks.add_task(
        scrape_main,
        request.company,
        request.pincodes,
        city_map,
        request.sendMailFlag,
        request.recipient_email,
        request.getCompetitorFlag,
        request.getProductTitleFlag,
        request.asins,
        request.includePrice,
        request.includeSellerCount
    )

    return {"message": "Scraping started in background"}
