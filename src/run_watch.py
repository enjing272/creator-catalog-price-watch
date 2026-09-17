import argparse
import json

from price_watch import CatalogItem, CompetitorOffer, InfraiClient, choose_offer, evaluate_price


def main() -> None:
    parser = argparse.ArgumentParser(description="Check one creator catalog item against supplied offers.")
    parser.add_argument("--item", required=True, help="JSON: slug,title,current_price,subscriber_id")
    parser.add_argument("--offers", required=True, help="JSON list with vendor,title,price,url")
    args = parser.parse_args()
    item = CatalogItem(**json.loads(args.item))
    offers = [CompetitorOffer(**row) for row in json.loads(args.offers)]
    selected = choose_offer(InfraiClient(), item, offers)
    print(json.dumps(evaluate_price(item, selected).__dict__, default=lambda value: value.__dict__, sort_keys=True))


if __name__ == "__main__":
    main()
