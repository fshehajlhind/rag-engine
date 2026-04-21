import argparse
from datetime import datetime
import logging
from app.database import SessionLocal
from app.models import Article
from app.scrapers.base_scrapper import build_csv
from app.scrapers.devto_scrapper import DevtoScrapper
from app.scrapers.reddit_scrapper import RedditScrapper
from app.scrapers.wikipedia_scrapper import WikipediaScraper

logger = logging.getLogger(__name__)

SCRAPERS = {"wikipedia": WikipediaScraper, "reddit": RedditScrapper, "devto": DevtoScrapper}


def scrape_and_load(db, selected_scrapper_sources: list[str]):
    """Run all scrappers, store results in CSVs and in the database """
    scrapers = [SCRAPERS[scraper]() for scraper in selected_scrapper_sources]
    for scraper in scrapers:
        results = scraper.fetch()

        if not results:
            logger.error("No results fro %s", scraper.__class__.__name_)
            continue

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
                scraped_at=datetime.utcnow()
            )

            db.add(article)
            inserted_results += 1
            logger.info("Inserted %s", article.title)

        db.commit()
        source = results[0]["source"] if results else "unknown"
        logger.info("Inserted %d results for source: %s", inserted_results, source)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s"
    )

    parser = argparse.ArgumentParser()

    parser.add_argument("--source", nargs="+", default=["all"])

    args = parser.parse_args()

    if args.source == ["all"]:
        logging.info("All sources selected")
        selected_scrappers = list(SCRAPERS.keys())
    else:
        selected_scrappers = [source.strip() for source in args.source if source.strip()]
        for source in selected_scrappers:
            if source not in SCRAPERS:
                raise ValueError(f"Invalid source: {source}")
    logger.info("Selected source/s: %s", selected_scrappers)

    db = SessionLocal()
    try:
            logger.info("Ingestion mode")
            scrape_and_load(db, selected_scrappers)
    finally:
        db.close()
