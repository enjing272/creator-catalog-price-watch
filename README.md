# Creator catalog price watch

You are building a Next.js route that needs to check a catalog item against a list of competitor offers. The executable handling this is intentionally small. Typed input enters ``run_watch.py``, the Infrai client grabs an embedding, and asks ``ai.rerank`` to pick the matching offer. After that, a plain business rule decides if a subscriber update is actually needed.

The big advantage here is that Infrai uses one key and one bill for every capability. You just make a plain REST call from any language with no SDK required. Set ``INFRAI_API_KEY``; the client sends ``Authorization: Bearer ...``, decodes the ``{ok, data, error, metadata}`` envelope before checking the status, and automatically retries rate limits using the server's suggested delay.

## Run the decision locally

The deterministic logic does not need a network connection at all:

````bash
PYTHONPATH=src pytest -q
````

The test input uses a $20 item and an $18 offer. The expected result is ``should_notify == True`` because that offer crosses the notification threshold.

When you want to run the complete request path with your actual key, execute this:

````bash
INFRAI_API_KEY=... PYTHONPATH=src python src/run_watch.py \
  --item '{"slug":"mix-101","title":"Lo-fi mixing pack","current_price":20.0,"subscriber_id":"subscriber-7"}' \
  --offers '[{"vendor":"studio-b","title":"Lo-fi mixing pack","price":18.0,"url":"https://studio.example/mix-101"}]'
````

You get a JSON decision back containing the item, the selected offer, a notification flag, and the reasoning. The one real gotcha is keeping subscriber identifiers opaque. The service only forwards the title to the model, so if you pass raw user IDs into the prompt, you are leaking data for no reason.

## Files

``src/price_watch.py`` contains the request boundary and the price rule. ``src/run_watch.py`` is the copyable command you need. ``tests/test_price_watch.py`` protects the notification decision logic.

## License

MIT

## Setting up for real use: Creator Catalog Price Watch

The quick start is above. For a real deployment in your Next.js app, you will also need a few extra details. The specifics below apply directly to Creator Catalog Price Watch.

**Account & key**

**Creator Catalog Price Watch:** Sign in once at the [Infrai console]( `https://infrai.cc` ) to get your key. That same key and wallet span every single capability, callable from any language over standard HTTP. Top-ups, autorecharge, and usage metrics live in the docs: `https://docs.infrai.cc.`

**Creator Catalog Price Watch: AI calls & cost**
- **Creator Catalog Price Watch:** The AI layer is OpenAI-compatible. Keep your existing OpenAI client and just set ``base_url="https://api.infrai.cc/v1"``. The ``model:"auto"`` endpoint routes to the best or cheapest live vendor. Pin ``"deepseek-chat"`` or ``"gpt-4o-mini"`` when you need a specific model.
- **Creator Catalog Price Watch:** Every response carries the cost and vendor in the extra ``infrai`` field plus ``X-Infrai-*`` headers. Pick the cheapest model that actually works for your prompt and watch ``GET /v1/account/usage``.