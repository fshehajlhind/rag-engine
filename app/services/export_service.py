import json

import pandas as pd
from app.services.articles_service import get_articles_dict


def export_files(output_format: str, db):
    articles = get_articles_dict(db)["articles"]
    return (export_jsonl(articles), "application/x-ndjson") if output_format == "jsonl" else (export_csv(articles), "text/csv")


def export_csv(articles: list[dict]) -> str:
    df = pd.DataFrame(articles)

    columns = ["uuid", "title", "url", "source", "content", "author"]

    for column in columns:
        if column not in df.columns:
            df[column] = ""

    return df[columns].to_csv(index=False)


def export_jsonl(articles: list[dict]) -> str:
    return "\n".join(
        json.dumps(article, ensure_ascii=False)
        for article in articles
    )
