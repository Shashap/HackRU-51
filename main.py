import asyncio
import nest_asyncio
from datetime import datetime
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List
from fastapi import FastAPI, Request
import scrape
import database
from scrape_classes import SearchResult, StopSearch

app = FastAPI()
nest_asyncio.apply()
templates = Jinja2Templates(directory="templates")
database.create_tables()
database.clear_search_tables()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/past_searches", response_class=HTMLResponse)
async def past_searches(request: Request):
    return templates.TemplateResponse("past_searches.html", {"request": request})


def fetch_search_results(query: str) -> List[SearchResult]:
    rows = database.get_search_results(query)
    return [SearchResult(**{k: row[i] for i, k in enumerate(SearchResult.__fields__.keys())}) for row in rows]


@app.get("/search_check", response_model=StopSearch)
async def search_check():
    ge_10_rows = database.check_10_rows(True)
    return {"stop": ge_10_rows}


@app.get("/search")
async def search(query: str) -> List[SearchResult]:
    time = datetime.now()
    database.insert_new_query(query, time)
    scrape.scrape_amazon_com(query)
    return fetch_search_results(query)


@app.get("/button_click")
async def button_click(name: str) -> SearchResult:
    search_result = database.get_row_by_pk_search_results(name)
    asin = search_result.ASIN
    if asin:
        asyncio.run(scrape.async_scrape_amazon(name))
    else:
        asyncio.run(scrape.async_scrape_amazon(name, False))
    query = database.update_results_history(name)
    return fetch_search_results(query)[0]


@app.get("/fetch_past_searches")
async def fetch_past_searches() -> List[SearchResult]:
    rows = database.get_results_history()
    return [SearchResult(**{k: row[i] for i, k in enumerate(SearchResult.__fields__.keys())}) for row in rows]
