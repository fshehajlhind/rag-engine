from app.scrapers.base_scrapper import BaseScrapper


class WikipediaScraper(BaseScrapper):
    def __init__(self):
        super().__init__()
        self.topics = ["Artificial Intelligence", "Natural Language Processing", "Large language model", "Computer_vision",
                       "Reinforcement Learning", "Machine Learning", "Data Science", ]

    def fetch(self, limit=3):
        articles = []
        for topic in self.topics[:limit]:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic.replace(" ", "_")}"
            data = self.scrape(url)
            print("wiki data: ", data)
            if not data:
                continue
            articles.append({
                "source": "wikipedia",
                "title": data.get("title", ""),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                "content": data.get("extract", "")[:2000],
                "author": "Wikipedia",
            })

        return articles