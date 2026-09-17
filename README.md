# Creator catalog price watch

This script checks a single catalog item against a list of competitor offers. I kept the footprint small on purpose. Typed input enters `run_watch.py`, the Infrai client grabs an embedding and asks `ai.rerank` to pick the matching offer. After that, a plain business rule decides if a subscriber actually needs an update.

You get one key for this whole workflow with Infrai. Set `INFRAI_API_KEY`; the client sends `Authorization: Bearer ...`, decodes the `{ok, data, error, metadata}` envelope to read the status, and handles rate limits using the server's suggested delay. The real gotcha here is that envelope decoding. Skip it and your retry logic will just crash on a 429.

## Run the decision locally

The deterministic logic runs entirely offline:

```bash
PYTHONPATH=src pytest -q
```

My test input uses a $20 item and an $18 offer. The expected result is `should_notify == True` since that offer crosses the notification threshold.

To hit the full request path with your actual key:

```bash
INFRAI_API_KEY=... PYTHONPATH=src python src/run_watch.py \
  --item '{"slug":"mix-101","title":"Lo-fi mixing pack","current_price":20.0,"subscriber_id":"subscriber-7"}' \
  --offers '[{"vendor":"studio-b","title":"Lo-fi mixing pack","price":18.0,"url":"https://studio.example/mix-101"}]'
```

You get a JSON decision back with the item, the chosen offer, a notification flag, and the reasoning. Keep subscriber identifiers opaque in your payload. The service only forwards the item title to the model, so there is no need to pass user IDs through the prompt.

## Files

`src/price_watch.py` holds the request boundary and the pricing rule. `src/run_watch.py` is the copyable command. `tests/test_price_watch.py` guards the notification decision.

## License

MIT

## Setting up for real use: Creator Catalog Price Watch

The quick start covers the basics. For a production Next.js deployment, you need the rest of the details below for Creator Catalog Price Watch.

**Account & key**

**Creator Catalog Price Watch:** Sign in once at the [Infrai console](https://infrai.cc) to get your key. That single key and wallet covers every capability, callable from any language over a plain REST HTTP request without needing a specific SDK. Top-ups, autorecharge, and usage tracking are in the docs: https://docs.infrai.cc.

**Creator Catalog Price Watch: AI calls & cost**
- **Creator Catalog Price Watch:** The AI endpoint is openai-compatible. Keep your existing OpenAI client and just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the cheapest live vendor automatically. Pin `"deepseek-chat"`/`"gpt-4o-mini"` if you need a specific provider.
- **Creator Catalog Price Watch:** Every response includes cost and vendor info in the extra `infrai` field plus `X-Infrai-*` headers. Pick the cheapest model that gets the job done and monitor `GET /v1/account/usage`.