import pandas as pd
import datetime
import os
import re
from bs4 import BeautifulSoup
import requests
from langchain_community.document_loaders import WebBaseLoader
from urllib.parse import urljoin, urlparse
import time
from typing import List, Set, Optional
import logging

logger = logging.getLogger(__name__)

def parse_data(
    link: str,
    max_pages: int = 50,
    max_depth: int = 3,
    timeout: int = 10,
    same_domain_only: bool = True
) -> List[str]:
    """
    Recursively parse and extract content from a website.
    
    Args:
        link: Starting URL to crawl
        max_pages: Maximum number of pages to crawl (default: 50)
        max_depth: Maximum depth of recursion (default: 3)
        timeout: Request timeout in seconds (default: 10)
        same_domain_only: Only crawl URLs from the same domain (default: True)
    
    Returns:
        List of extracted text content from each page
    """
    visited = set()
    to_visit = [(link, 0)]  # (url, depth)
    to_visit_urls = {link}  # Set for O(1) lookup
    all_data = []
    
    base_domain = urlparse(link).netloc
    
    def sanitize_filename(url):
        """Sanitize URL to create a valid filename."""
        return re.sub(r'[\\/*?:"<>|]', "", url).replace("https://", "").replace("http://", "").replace("/", "")
    
    def get_page_links(url: str, current_depth: int) -> List[tuple]:
        """
        Extract all links from a page.
        
        Args:
            url: URL to extract links from
            current_depth: Current depth in the crawl tree
            
        Returns:
            List of tuples (url, depth)
        """
        try:
            response = requests.get(url, timeout=timeout, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            links = []
            for a_tag in soup.find_all('a', href=True):
                href = a_tag.get('href')
                
                # Convert relative URLs to absolute
                full_url = urljoin(url, href)
                
                # Parse the URL
                parsed_url = urlparse(full_url)
                
                # Skip non-HTTP(S) URLs
                if parsed_url.scheme not in ['http', 'https']:
                    continue
                
                # Only include URLs from the same domain if required
                if same_domain_only and parsed_url.netloc != base_domain:
                    continue
                
                # Remove fragments
                clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                if parsed_url.query:
                    clean_url += f"?{parsed_url.query}"
                
                links.append((clean_url, current_depth + 1))
            
            return links
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error fetching links from {url}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching links from {url}: {e}")
            return []
    
    def extract_content(url: str) -> Optional[str]:
        """
        Extract text content from a URL.
        
        Args:
            url: URL to extract content from
            
        Returns:
            Extracted text content or None if extraction fails
        """
        try:
            loader = WebBaseLoader(url)
            data = loader.load()
            return data[0].page_content if data else None
        except Exception as e:
            logger.warning(f"Error extracting content from {url}: {e}")
            return None
    
    # Crawl the website (breadth-first approach)
    logger.info(f"Starting recursive crawl from: {link}")
    logger.info(f"Max pages: {max_pages}, Max depth: {max_depth}")
    
    while to_visit and len(visited) < max_pages:
        current_url, current_depth = to_visit.pop(0)
        to_visit_urls.discard(current_url)  # Remove from set
        
        # Skip if already visited
        if current_url in visited:
            continue
        
        # Skip if exceeding max depth
        if current_depth > max_depth:
            continue
            
        logger.info(f"Processing [{len(visited)+1}/{max_pages}] (depth {current_depth}): {current_url}")
        visited.add(current_url)
        
        # Get content from the current URL
        content = extract_content(current_url)
        if content:
            all_data.append(content)
            logger.debug(f"Extracted {len(content)} characters from {current_url}")
        
        # Only get links if we haven't reached max depth
        if current_depth < max_depth:
            # Get links from the current URL
            new_links = get_page_links(current_url, current_depth)
            for new_link, depth in new_links:
                if new_link not in visited and new_link not in to_visit_urls:
                    to_visit.append((new_link, depth))
                    to_visit_urls.add(new_link)
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.5)
    
    logger.info(f"Crawl complete: Found {len(all_data)} pages with content from {len(visited)} URLs")
    
    return all_data