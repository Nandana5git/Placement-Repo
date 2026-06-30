from .models import Notification
from .tasks import send_email_notification_task

def send_system_notification(user, title, message, send_email=True):
    """
    Creates an in-app notification and enqueues an email notification task.
    Includes a fail-safe fallback to send synchronously if Celery is down.
    """
    # Create DB notification
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message
    )

    if send_email and user.email:
        try:
            # Trigger celery async task
            send_email_notification_task.delay(user.email, title, message)
        except Exception as e:
            # Fallback to synchronous execution if broker is not running
            print(f"[Warning] Celery broker connection failed: {e}. Executing email task synchronously.")
            send_email_notification_task(user.email, title, message)

    return notification
