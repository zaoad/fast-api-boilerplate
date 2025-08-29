import time
from app.core.celery import celery_app

@celery_app.task(bind=True, name="app.tasks.linkedin.process_linkedin_task")
def process_linkedin_task(self, task_data: dict):
    """
    Process a LinkedIn task in the background
    This is a sample implementation that simulates work by sleeping
    """
    # Simulate some work
    time.sleep(5)
    
    result = {
        "task_data": task_data,
        "status": "completed",
        "message": "LinkedIn task processed successfully"
    }
    print("--------------------------------")
    print(result)
    print("--------------------------------")