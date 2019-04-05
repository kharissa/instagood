web: python migrate.py; gunicorn start:app --preload;
worker: rq worker --url $REDIS_URL