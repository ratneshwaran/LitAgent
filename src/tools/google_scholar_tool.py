"""
Google Scholar search tool using web scraping
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Dict, Any
from ..models import Paper, SearchFilters
from ..utils.logging import get_logger

logger = get_logger(__name__)

def search_google_scholar(query: str, filters: SearchFilters) -> List[Paper]:
    """Search Google Scholar using web scraping"""
    try:
        # Google Scholar search URL
        url = "https://scholar.google.com/scholar"
        
        params = {
            "q": query,
            "hl": "en",
            "as_sdt": "0,5"
        }
        
        # Add year filters if specified
        if filters.start_year and filters.end_year:
            params["as_ylo"] = str(filters.start_year)
            params["as_yhi"] = str(filters.end_year)
        elif filters.start_year:
            params["as_ylo"] = str(filters.start_year)
        elif filters.end_year:
            params["as_yhi"] = str(filters.end_year)
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        papers = []
        
        # Find all paper entries
        entries = soup.find_all('div', class_='gs_ri')
        
        for entry in entries[:min(filters.limit, 20)]:  # Limit to avoid rate limiting
            try:
                # Extract title and link
                title_elem = entry.find('h3', class_='gs_rt')
                if not title_elem:
                    continue
                
                title_link = title_elem.find('a')
                if title_link:
                    title = title_link.get_text().strip()
                    url = title_link.get('href', '')
                else:
                    title = title_elem.get_text().strip()
                    url = ''
                
                # Extract authors and venue
                authors_venue = entry.find('div', class_='gs_a')
                authors = []
                venue = ""
                year = None
                
                if authors_venue:
                    text = authors_venue.get_text()
                    # Extract year
                    year_match = re.search(r'\b(19|20)\d{2}\b', text)
                    if year_match:
                        year = int(year_match.group())
                    
                    # Split by common separators
                    parts = re.split(r'[,\-–]', text)
                    if len(parts) >= 2:
                        authors = [part.strip() for part in parts[:-1] if part.strip()]
                        venue = parts[-1].strip()
                
                # Extract abstract
                abstract_elem = entry.find('div', class_='gs_rs')
                abstract = abstract_elem.get_text().strip() if abstract_elem else ""
                
                # Extract citation count
                citations = 0
                cited_elem = entry.find('a', href=re.compile(r'cites='))
                if cited_elem:
                    cited_text = cited_elem.get_text()
                    cited_match = re.search(r'Cited by (\d+)', cited_text)
                    if cited_match:
                        citations = int(cited_match.group(1))
                
                # Extract PDF link
                pdf_url = None
                pdf_elem = entry.find('a', href=re.compile(r'\.pdf'))
                if pdf_elem:
                    pdf_url = pdf_elem.get('href')
                
                paper = Paper(
                    id=url or title,
                    source="scholar",
                    title=title,
                    abstract=abstract,
                    authors=authors,
                    venue=venue,
                    year=year,
                    doi=None,  # Google Scholar doesn't provide DOI directly
                    url=url,
                    pdf_url=pdf_url,
                    citations_count=citations,
                    keywords=[]
                )
                papers.append(paper)
                
            except Exception as e:
                logger.warning(f"Error parsing Google Scholar paper: {e}")
                continue
        
        logger.info(f"Google Scholar returned {len(papers)} papers")
        return papers
        
    except Exception as e:
        logger.error(f"Google Scholar search failed: {e}")
        return []
