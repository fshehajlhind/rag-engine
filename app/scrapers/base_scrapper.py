import csv
import logging
import time
from pathlib import Path

import requests


def build_csv(results: list[dict]):
    logging.info("Building CSV...")

    if not results:
        logging.info("Data invalid or missing")
        return
    fieldnames = results[0].keys()
    website = results[0].get("source")
    root_dir = Path(__file__).resolve().parents[2]
    with open(root_dir / "data" / f"{website}.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    logging.info("CSV generated")


class BaseScrapper(object):

    def __init__(self):
        self.headers = {"User-Agent": "RAGSearchBot/1.0"}

    def scrape(self, url):
        logging.info("Scraping %s", url)
        max_retries = 5
        backoff = 1
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                logging.info("Status code: %d", response.status_code)

                if response.status_code == 200:
                    return response.json()

                if response.status_code == 429:
                    retry_time = backoff * (2 ** attempt)
                    logging.info("Received HTTP 429, retrying in: %d seconds", retry_time)
                    time.sleep(retry_time)
                    continue

                logging.error("Received status code %d, error: %s ", response.status_code, response.reason)
                return None
            except requests.RequestException as e:
                logging.error("Request exception %s", e)
                return None

        logging.info("Max retries for url: %s reached. Received HTTP 429 Too Many Requests.", url)
        return None
