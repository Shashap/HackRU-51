from pydantic import BaseModel
from typing import Optional


class SearchResult(BaseModel):
    ASIN: Optional[str]
    Name: str
    Query: str
    Image: Optional[str]
    Rating: Optional[float]
    Price_Amazon_com: float
    Link_Amazon_com: str
    Price_Amazon_ca: Optional[float]
    Link_Amazon_ca: Optional[str]
    Price_Amazon_co_uk: Optional[float]
    Link_Amazon_co_uk: Optional[str]
    Price_Amazon_de: Optional[float]
    Link_Amazon_de: Optional[str]
    Time: Optional[object]


class StopSearch(BaseModel):
    stop: bool

