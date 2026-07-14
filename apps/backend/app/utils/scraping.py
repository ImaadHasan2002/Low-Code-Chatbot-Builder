from dataclasses import dataclass
from typing import Iterable, List, Optional
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


@dataclass
class CrawledPage:
    url: str
    title: str
    content: str
    depth: int
    status_code: int


def _normalize_url(url: str) -> str:
    clean_url, _fragment = urldefrag(url.strip())
    parsed = urlparse(clean_url)
    if not parsed.scheme:
        clean_url = f"https://{clean_url}"
        parsed = urlparse(clean_url)
    if parsed.path == "":
        clean_url = clean_url.rstrip("/") + "/"
    return clean_url


def _path_allowed(path: str, include_paths: Iterable[str], exclude_paths: Iterable[str]) -> bool:
    includes = [item.strip() for item in include_paths if item and item.strip()]
    excludes = [item.strip() for item in exclude_paths if item and item.strip()]

    if includes and not any(path.startswith(item) for item in includes):
        return False
    if excludes and any(path.startswith(item) for item in excludes):
        return False
    return True


def _extract_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    return " ".join(soup.get_text(separator=" ").split())


def crawl_site(
    base_url: str,
    *,
    max_pages: int = 25,
    max_depth: int = 2,
    include_paths: Optional[List[str]] = None,
    exclude_paths: Optional[List[str]] = None,
    timeout: int = 10,
) -> List[CrawledPage]:
    """Crawl same-origin HTML pages breadth-first and return page metadata."""
    start_url = _normalize_url(base_url)
    parsed_base = urlparse(start_url)
    base_origin = parsed_base.netloc.lower()
    include_paths = include_paths or []
    exclude_paths = exclude_paths or []

    visited = set()
    queued = {start_url}
    queue = [(start_url, 0)]
    pages: List[CrawledPage] = []

    while queue and len(pages) < max_pages:
        current_url, depth = queue.pop(0)
        queued.discard(current_url)
        if current_url in visited or depth > max_depth:
            continue

        parsed_current = urlparse(current_url)
        if parsed_current.netloc.lower() != base_origin:
            continue
        if not _path_allowed(parsed_current.path or "/", include_paths, exclude_paths):
            continue

        visited.add(current_url)

        try:
            response = requests.get(
                current_url,
                timeout=timeout,
                headers={"User-Agent": "BotCraftCrawler/1.0"},
            )
            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type and content_type:
                continue
            soup = BeautifulSoup(response.text, "html.parser")
        except Exception as exc:
            print(f"Error crawling {current_url}: {exc}")
            continue

        title = soup.title.get_text(strip=True) if soup.title else current_url
        content = _extract_text(soup)
        if content:
            pages.append(
                CrawledPage(
                    url=current_url,
                    title=title or current_url,
                    content=content,
                    depth=depth,
                    status_code=response.status_code,
                )
            )

        if depth >= max_depth:
            continue

        for tag in soup.find_all("a", href=True):
            next_url = _normalize_url(urljoin(current_url, tag["href"]))
            parsed_next = urlparse(next_url)
            if parsed_next.netloc.lower() != base_origin:
                continue
            if next_url in visited or next_url in queued:
                continue
            if not _path_allowed(parsed_next.path or "/", include_paths, exclude_paths):
                continue
            queue.append((next_url, depth + 1))
            queued.add(next_url)

    return pages


def parse_data(link: str) -> List[str]:
    """Backward-compatible helper used by older code paths."""
    return [page.content for page in crawl_site(link, max_pages=2, max_depth=1)]
