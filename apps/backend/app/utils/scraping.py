import pandas as pd
import datetime
import os
import re
from bs4 import BeautifulSoup
import requests
from langchain_community.document_loaders import WebBaseLoader
from urllib.parse import urljoin, urlparse
import time

def parse_data(link):    
    visited = set()
    to_visit = [link]
    all_data = []
    
    base_domain = urlparse(link).netloc
    
    max_pages = 2  # Maximum pages to crawl
    timeout = 10    # Request timeout in seconds
    
    def sanitize_filename(url):
        return re.sub(r'[\\/*?:"<>|]', "", url).replace("https://", "").replace("http://", "").replace("/", "")
    
    def get_page_links(url):
        try:
            response = requests.get(url, timeout=timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            links = []
            for a_tag in soup.find_all('a', href=True):
                href = a_tag.get('href')
                
                # Convert relative URLs to absolute
                full_url = urljoin(url, href)
                
                # Only include URLs from the same domain
                if urlparse(full_url).netloc == base_domain:
                    links.append(full_url)
            
            return links
        except Exception as e:
            print(f"Error fetching links from {url}: {e}")
            return []
    
    def extract_content(url):
        try:
            loader = WebBaseLoader(url)
            data = loader.load()
            return data[0].page_content
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return ""
    
    # Crawl the website (breadth-first approach)
    print(f"Starting to crawl from: {link}")
    
    while to_visit and len(visited) < max_pages:
        current_url = to_visit.pop(0)
        
        if current_url in visited:
            continue
            
        print(f"Processing: {current_url}")
        visited.add(current_url)
        
        # Get content from the current URL
        content = extract_content(current_url)
        if content:
            all_data.append(content)
            
        # Get links from the current URL
        new_links = get_page_links(current_url)
        for new_link in new_links:
            if new_link not in visited and new_link not in to_visit:
                to_visit.append(new_link)
    
    print(f"Found {len(all_data)} pages with content")
    print(all_data)

    return all_data