import csv
import time
import requests


def build_csv(results):
    print("Building CSV...")

    if not results:
        print("Data invalid or missing")
        return
    fieldnames = results[0].keys()
    website = results[0].get("source")
    with open(f"../../data/{website}.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


class BaseScrapper(object):

    def __init__(self):
        self.headers = {"User-Agent": "RAGSearchBot/1.0"}

    def scrape(self, url):
        print("Scraping " + url)
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            print("Status code: " + str(response.status_code))
            if not response:
                return None

            if response.status_code == 429:
                time.sleep(10)
                response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code != 200:
                return None

            data = response.json()
            return data
        except requests.RequestException:
            return None
