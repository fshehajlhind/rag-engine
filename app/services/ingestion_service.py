from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import Base, Article
from app.scrapers.base_scrapper import build_csv
from app.scrapers.devto_scrapper import DevtoScrapper
from app.scrapers.reddit_scrapper import RedditScrapper
from app.scrapers.wikipedia_scrapper import WikipediaScraper

def scrape_and_load(db):
    scrapers = [WikipediaScraper(), RedditScrapper(), DevtoScrapper()]
    for scraper in scrapers:
        results = scraper.fetch()
        build_csv(results)
        inserted_results = 0
        for item in results:
            existing = db.query(Article).filter(Article.url == item["url"]).first()
            if existing:
                print("URL exists.")
                continue

            article = Article(
                source=item["source"],
                title=item["title"],
                url=item["url"],
                content=item["content"],
                author=item["author"],
            )

            db.add(article)
            inserted_results += 1
        db.commit()
        source = results[0]["source"] if results else "unknown"
        print(f"Inserted {inserted_results} results for source {source}")

if __name__ == "__main__":
    engine = create_engine("sqlite:///rag.db", echo=True)
    db = Session(engine)
    Base.metadata.create_all(engine)
    try:
        scrape_and_load(db)
    finally:
        db.close()


