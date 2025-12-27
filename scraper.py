import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Optional, Tuple
from datetime import datetime, timezone
from models import Link, Section


async def fetch_page(url: str) -> Tuple[str, str]:
    """Fetch page content using httpx."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0, headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text, str(response.url)


def extract_metadata(soup: BeautifulSoup, final_url: str) -> dict:
    """Extract title, description, language, and canonical URL from the page."""
    # Extract title
    title = None
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    
    # Extract description
    description = None
    meta_desc = soup.find("meta", attrs={"name": "description"}) or \
                soup.find("meta", attrs={"property": "og:description"})
    if meta_desc and meta_desc.get("content"):
        description = meta_desc["content"].strip()
    
    # Extract language
    language = None
    if soup.html and soup.html.get("lang"):
        language = soup.html["lang"]
    
    # Extract canonical URL
    canonical_url = None
    canonical = soup.find("link", attrs={"rel": "canonical"})
    if canonical and canonical.get("href"):
        canonical_url = urljoin(final_url, canonical["href"])
    
    return {
        "title": title,
        "description": description,
        "language": language,
        "canonicalUrl": canonical_url
    }


def extract_links(element, base_url: str) -> List[Link]:
    """Extract all links from an element and convert to absolute URLs."""
    links = []
    for a_tag in element.find_all("a", href=True):
        text = a_tag.get_text(strip=True)
        href = a_tag["href"]
        absolute_url = urljoin(base_url, href)
        links.append(Link(text=text, url=absolute_url))
    return links


def extract_sections(soup: BeautifulSoup, base_url: str) -> List[Section]:
    """Extract content grouped by HTML landmarks (header, nav, main, section, footer)."""
    sections = []
    landmark_tags = ["header", "nav", "main", "section", "footer"]
    
    for tag_name in landmark_tags:
        elements = soup.find_all(tag_name)
        for element in elements:
            # Extract text content and strip extra whitespace
            content = element.get_text(separator=" ", strip=True)
            # Remove extra whitespace (multiple spaces, tabs, newlines)
            content = " ".join(content.split())
            # Limit to 2,000 characters
            if len(content) > 2000:
                content = content[:2000]
            
            # Extract links
            links = extract_links(element, base_url)
            
            # Only add section if it has content
            if content:
                sections.append(Section(
                    tag=tag_name,
                    content=content,
                    links=links
                ))
    
    return sections


def truncate_html(html: str, max_length: int = 10000) -> dict:
    """Truncate HTML to specified length and return with truncated flag."""
    truncated = len(html) > max_length
    html_content = html[:max_length] if truncated else html
    return {
        "html": html_content,
        "truncated": truncated
    }


async def scrape_url(url: str) -> dict:
    """Main scraping function that coordinates all extraction."""
    # Capture timestamp
    scraped_at = datetime.now(timezone.utc).isoformat()
    
    # Fetch the page
    html_content, final_url = await fetch_page(url)
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Extract metadata
    metadata = extract_metadata(soup, final_url)
    
    # Extract sections
    sections = extract_sections(soup, final_url)
    
    # Truncate raw HTML
    raw_html = truncate_html(html_content)
    
    # Create interactions object (placeholder for static scraping)
    interactions = {
        "clicks": [],
        "scrolls": 0,
        "pages": [final_url]
    }
    
    return {
        "url": final_url,
        "scrapedAt": scraped_at,
        "meta": {
            "title": metadata["title"],
            "description": metadata["description"],
            "language": metadata["language"],
            "canonicalUrl": metadata["canonicalUrl"]
        },
        "rawHtml": raw_html,
        "sections": sections,
        "interactions": interactions
    }
