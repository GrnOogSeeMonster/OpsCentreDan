# Worker

Worker process runs from the API image and executes Celery tasks.

Local command:

```bash
celery -A app.tasks.celery_app.celery_app worker -l info
```
