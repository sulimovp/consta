# Extractor model pin

The LLM feature extractor (`consta/predict/extractor.py`) is pinned to one model so that
extracted rows stay comparable. Captured 2026-08-30:

| Field | Value |
|-------|-------|
| Hub model | `openai/gpt-oss-120b` |
| Hub revision | `b5c939de8f754692c1647ca79fbf85e8c1e70f8a` |
| Router id | `openai/gpt-oss-120b:groq` |

The Hugging Face router does not accept a revision, so the call uses the router id and
the revision is recorded next to it. `:fastest` is a routing alias, not a model, and must
not be used for extraction.

Files:

- `extractor_pin.json`: the pin, read by the extractor tests.
- `gpt-oss-120b-card.json`: the Hub model card at that revision.
- `router_models.json`: the router's model catalogue on that day.
