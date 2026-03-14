from celery import Celery
import time

celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)


@celery_app.task
def train_model_task():
    # Simulate training (replace with ML pipeline)
    time.sleep(5)
    return {"status": "model trained", "version": "v1.0"}
