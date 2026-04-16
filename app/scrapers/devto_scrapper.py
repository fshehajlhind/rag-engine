import logging
import time
from app.scrapers.base_scrapper import BaseScrapper


class DevtoScrapper(BaseScrapper):
    def __init__(self):
        super().__init__()
        self.topics = ["machinelearning", "ai", "webdev"]

    def fetch(self, limit=5, per_page: int = 30):
        articles = []
        for tag in self.topics[:limit]:
            url = f"https://dev.to/api/articles?tag={tag}&per_page={per_page}"
            response = self.scrape(url)
            if not response:
                logging.info(f"Skipping tag '{tag}'")
                continue
            for item in response:
                articles.append({
                    "source": "devto",
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("description", "")[:2000],
                    "author": item.get("user", {}).get("name", ""),
                })
            time.sleep(0.3)
        return articles