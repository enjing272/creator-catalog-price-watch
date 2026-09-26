from price_watch import CatalogItem, CompetitorOffer, InfraiClient, evaluate_price


def test_notification_marks_material_price_drop():
    item = CatalogItem("mix-101", "Lo-fi mixing pack", 20.0, "subscriber-7")
    offer = CompetitorOffer("studio-b", "Lo-fi mixing pack", 18.0, "https://studio.example/mix-101")
    result = evaluate_price(item, offer)
    assert result.should_notify is True
    assert result.reason == "offer crosses notification threshold"


def test_rerank_uses_default_vendor(monkeypatch):
    client = InfraiClient(api_key="test-key")
    request = {}

    def fake_post(path, payload):
        request.update(path=path, payload=payload)
        return {"results": [{"index": 1}]}

    monkeypatch.setattr(client, "_post", fake_post)

    assert client.rerank("mixing pack", ["mastering", "mixing"]) == 1
    assert request == {
        "path": "/v1/ai/rerank",
        "payload": {
            "query": "mixing pack",
            "candidates": ["mastering", "mixing"],
            "top_k": 1,
            "model": "auto",
        },
    }
