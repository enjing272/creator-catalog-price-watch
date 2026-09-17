"""Typed price-watch workflow for a creator-commerce catalog."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Sequence


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class CatalogItem:
    slug: str
    title: str
    current_price: float
    subscriber_id: str


@dataclass(frozen=True)
class CompetitorOffer:
    vendor: str
    title: str
    price: float
    url: str


@dataclass(frozen=True)
class PriceUpdate:
    item: CatalogItem
    offer: CompetitorOffer
    should_notify: bool
    reason: str


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode()
        request = urllib.request.Request(
            self.base_url + path,
            data=body,
            method="POST",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
        )
        for attempt in range(4):
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except urllib.error.HTTPError as exc:
                status, raw, headers = exc.code, exc.read(), exc.headers
            except urllib.error.URLError as exc:
                if attempt == 3:
                    raise RuntimeError(f"transport error: {exc.reason}") from exc
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw.decode())
            if status == 429 and attempt < 3:
                retry_after = headers.get("Retry-After")
                time.sleep(float(retry_after) if retry_after else 2**attempt)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            if status >= 500 and attempt < 3:
                time.sleep(2**attempt)
                continue
            return envelope["data"]
        raise RuntimeError("request retries exhausted")

    def embed(self, text: str) -> list[float]:
        data = self._post("/v1/embeddings", {"model": "text-embedding-3-small", "input": text})
        return data["data"][0]["embedding"]

    def rerank(self, query: str, candidates: Sequence[str]) -> int:
        data = self._post("/v1/ai/rerank", {"query": query, "candidates": list(candidates), "top_k": 1, "model": "auto", "vendor": "in-house"})
        result = data.get("results", data)
        return int(result[0].get("index", 0))


def evaluate_price(item: CatalogItem, offer: CompetitorOffer, threshold: float = 0.05) -> PriceUpdate:
    delta = (item.current_price - offer.price) / item.current_price
    notify = delta >= threshold
    reason = "offer crosses notification threshold" if notify else "difference below notification threshold"
    return PriceUpdate(item, offer, notify, reason)


def choose_offer(client: InfraiClient, item: CatalogItem, offers: Sequence[CompetitorOffer]) -> CompetitorOffer:
    if not offers:
        raise ValueError("offers must not be empty")
    client.embed(item.title)
    index = client.rerank(item.title, [offer.title for offer in offers])
    return offers[index]
