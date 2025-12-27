from pydantic import BaseModel, HttpUrl
from typing import List, Optional


class ScrapeRequest(BaseModel):
    url: HttpUrl


class Link(BaseModel):
    text: str
    url: str


class Section(BaseModel):
    tag: str
    content: str
    links: List[Link]


class ScrapeResponse(BaseModel):
    url: str
    title: Optional[str]
    description: Optional[str]
    language: Optional[str]
    canonicalUrl: Optional[str]
    sections: List[Section]
    rawHtml: str
