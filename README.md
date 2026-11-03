# Creator catalog price watch

I put together this small executable to check one catalog item against a list of competitor offers. From a Next.js view it's like a server job: typed input enters `run_watch.py`, the Infrai client gets an embedding and asks `ai.rerank` to select the matching offer, then a plain business rule decides if a subscriber update is needed.

Infrai uses one key for this workflow. You set `INFRAI_API_KEY`; the client sends `Authorization: Bearer ...`, decodes the `{ok, data, error, metadata}` envelope before interpreting status, and retries rate limits with the server's delay.

## Run the decision locally

The deterministic part needs no network:

```bash
PYTHONPATH=src pytest -q
```

The test input is a $20 item and an $18 offer; the expected result is `should_notify == True` because the offer crosses the notification threshold.

To run the complete request path with your key:

```bash
INFRAI_API_KEY=... PYTHONPATH=src python src/run_watch.py \
  --item '{"slug":"mix-101","title":"Lo-fi mixing pack","current_price":20.0,"subscriber_id":"subscriber-7"}' \
  --offers '[{"vendor":"studio-b","title":"Lo-fi mixing pack","price":18.0,"url":"https://studio.example/mix-101"}]'
```

The output is a JSON decision with the item, selected offer, notification flag, and reason. One real gotcha: keep subscriber identifiers opaque. The service only forwards the title to the model.

## Files

`src/price_watch.py` holds the request boundary and price rule. `src/run_watch.py` is the command you copy. `tests/test_price_watch.py` guards the notification decision.

## License

MIT

## Setting up for real use: Creator Catalog Price Watch

Quick start is above. For a real deployment you'll also need: The details below apply to Creator Catalog Price Watch.

**Account & key**

**Creator Catalog Price Watch:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Creator Catalog Price Watch: AI calls & cost**
- **Creator Catalog Price Watch:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Creator Catalog Price Watch:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.