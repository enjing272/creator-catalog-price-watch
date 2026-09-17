from price_watch import CatalogItem, CompetitorOffer, evaluate_price


def test_notification_marks_material_price_drop():
    item = CatalogItem("mix-101", "Lo-fi mixing pack", 20.0, "subscriber-7")
    offer = CompetitorOffer("studio-b", "Lo-fi mixing pack", 18.0, "https://studio.example/mix-101")
    result = evaluate_price(item, offer)
    assert result.should_notify is True
    assert result.reason == "offer crosses notification threshold"
