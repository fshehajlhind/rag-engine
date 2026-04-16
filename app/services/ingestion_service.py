import logging
from app.database import SessionLocal
from app.models import Article
from app.scrapers.base_scrapper import build_csv
from app.scrapers.devto_scrapper import DevtoScrapper
from app.scrapers.reddit_scrapper import RedditScrapper
from app.scrapers.wikipedia_scrapper import WikipediaScraper
from app.services.embedding_service import embed_all_articles

logger = logging.getLogger(__name__)

def scrape_and_load(db):
    """Run all scrappers, store results in CSVs and in the database """
    scrapers = [WikipediaScraper(), RedditScrapper(), DevtoScrapper()]
    for scraper in scrapers:
        results = scraper.fetch()
        build_csv(results)
        inserted_results = 0
        for item in results:
            existing = db.query(Article).filter(Article.url == item["url"]).first()
            if existing:
                logger.info("URL %s exists.", item["url"])
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
            logger.info(f"Inserted {article}")

        db.commit()
        source = results[0]["source"] if results else "unknown"
        logger.info(f"Inserted {inserted_results} results for source {source}")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s"
    )

    db = SessionLocal()
    try:
        scrape_and_load(db)
        embed_all_articles(db)
    finally:
        db.close()


