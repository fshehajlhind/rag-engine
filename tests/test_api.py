def test_get_articles(client):
    response = client.get("/articles")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["total_count"] == 2


def test_get_articles_paginated(client):
    response = client.get("/articles?page_size=1&page=2")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["total_count"] == 2
    assert len(response_json["articles"]) == 1
    assert response_json["articles"][0]["url"] == "https://reddit.com/wiki/Artificial_Intelligence"


def test_get_article_by_id_not_found(client):
    response = client.get("/articles/invalid-id")
    assert response.status_code == 404


def test_get_artice_by_id_found(client):
    all_articles_response = client.get("/articles?page=1&page_size=1")
    assert all_articles_response.status_code == 200

    all_articles_json = all_articles_response.json()["articles"]
    uuid = all_articles_json[0]["uuid"]
    get_by_id_response = client.get(f"/articles/{uuid}")
    assert get_by_id_response.status_code == 200
    article = get_by_id_response.json()
    assert article["uuid"] == uuid

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {"message": "OK"}


def test_get_stats(client):
    response = client.get("/stats")
    assert response.status_code == 200

    response_json = response.json()
    assert response_json["stats"] == [
        {
            "count": 1,
            "source": "reddit",
        },
        {
            "count": 1,
            "source": "wikipedia",
        },
    ]
