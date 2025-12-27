from fastapi import FastAPI, HTTPException
from models import ScrapeRequest, ScrapeResponse
from scraper import scrape_url

app = FastAPI()


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/scrape", response_model=ScrapeResponse)
async def scrape(request: ScrapeRequest):
    """
    Scrape a URL and extract structured content including:
    - Page metadata (title, description, language, canonical URL)
    - Sections grouped by HTML landmarks (header, nav, main, section, footer)
    - Links with absolute URLs
    - Truncated raw HTML
    """
    try:
        result = await scrape_url(str(request.url))
        return ScrapeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to scrape URL: {str(e)}")
