from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime


class ScrapeRequest(BaseModel):
    url: HttpUrl


class Link(BaseModel):
    text: str
    url: str


class Section(BaseModel):
    tag: str
    content: str
    links: List[Link]


class Meta(BaseModel):
    title: Optional[str]
    description: Optional[str]
    language: Optional[str]
    canonicalUrl: Optional[str]


class RawHtml(BaseModel):
    html: str
    truncated: bool


class Interactions(BaseModel):
    clicks: List[str]
    scrolls: int
    pages: List[str]


class ScrapeResponse(BaseModel):
    url: str
    scrapedAt: str
    meta: Meta
    rawHtml: RawHtml
    sections: List[Section]
    interactions: Interactions
