from app.scrapers.base_scrapper import BaseScrapper


class RedditScrapper(BaseScrapper):
    def __init__(self):
        super().__init__()
        self.topics = ["MachineLearning", "artificial", "LLM"]

    def fetch(self, limit=5):
        articles = []
        for topic in self.topics[:limit]:
            url = f"https://www.reddit.com/r/{topic}/top.json?limit={limit}&t=month"
            response = self.scrape(url)
            if not response:
                continue
            posts = response.get("data", {}).get("children", [])
            for post in posts:
                data = post.get("data", {})
                body = data.get("selftext", "").strip()
                if not body or body == "[removed]":
                    continue
                article = {
                        "source": "reddit",
                        "title": topic,
                        "url": url,
                        "content": body[:2000],
                        "author": data.get("author", ""),
                    }
                articles.append(article)

        return articles