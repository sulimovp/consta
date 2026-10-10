# Deploying the web UI

```bash
pip install -e ".[web]" gunicorn
export CONSTA_FLASK_SECRET="$(openssl rand -hex 32)"
export CONSTA_GITHUB_TOKEN=...
export CONSTA_OPENAI_API_KEY=...    # or another LLM key

gunicorn --bind 0.0.0.0:5050 --workers 1 --threads 8 --timeout 120 \
  "consta.web.app:create_app()"
```

- A run takes 60–90 seconds, hence `--timeout 120`.
- Jobs are kept in memory in the process that started them, so run one worker and
  scale with threads. With several workers, a status request can reach a worker that
  does not know the job.
- `CONSTA_FLASK_SECRET` is required outside localhost.

Behind nginx:

```nginx
location / {
    proxy_pass http://127.0.0.1:5050;
    proxy_read_timeout 120s;
}
```
