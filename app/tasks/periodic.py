import random
from app.core.celery import celery_app

@celery_app.task(bind=True, name="app.tasks.periodic.test_periodic_task")
def test_periodic_task(self):
    """Test periodic task that generates a random number and returns it"""
    random_number = random.randint(1, 100)
    print(f"Periodic task executed! Generated random number: {random_number}")
    return random_number