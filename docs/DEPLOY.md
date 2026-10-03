# Deploying the web UI

## Development

```bash
cd consta
pip install -e ".[web]"
consta-web
```

## Production (gunicorn)

```bash
pip install -e ".[web]" gunicorn
export CONSTA_FLASK_SECRET="$(openssl rand -hex 32)"
export CONSTA_GITHUB_TOKEN=...
export CONSTA_OPENAI_API_KEY=...

gunicorn --bind 0.0.0.0:5050 --workers 2 --threads 4 --timeout 120 \
  "consta.web.app:create_app()"
```

- **timeout 120** — assessments can take 60–90s; background jobs still run in-process per worker.
- Set **CONSTA_FLASK_SECRET** — required outside localhost.
- For multiple workers, replace in-memory job store with Redis (not implemented yet).

## Reverse proxy

Nginx example:

```nginx
location / {
    proxy_pass http://127.0.0.1:5050;
    proxy_read_timeout 120s;
}
```
