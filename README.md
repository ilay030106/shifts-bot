# Shifts Bot

## Run Telegram client test

Use uv (recommended):

```bash
uv run -m tests.test_telegram_client
```

Or Python:

```bash
python -m tests.test_telegram_client
```

Notes:

- Import path is configured via `sitecustomize.py`, so both forms work without editing sys.path.
- Ensure `TELEGRAM_BOT_TOKEN` is set in `.env`.
