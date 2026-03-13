import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Event, Task, Message

logger = logging.getLogger(__name__)

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def send_event_email(self, event_id):
    """
    Sends an email notification for a new Event.
    """
    try:
        event = Event.objects.get(id=event_id)
        subject = f"New Event: {event.title}"
        message_body = (
            f"A new event '{event.title}' has been created.\n\n"
            f"Start: {event.start_date}\n"
            f"End: {event.end_date}\n"
            f"Location: {event.location}\n\n"
            f"Description:\n{event.description}"
        )
        recipient_list = [event.owner.email] # Plus attendees if needed.  We will keep it simple here.
        if event.owner.email:
            send_mail(
                subject=subject,
                message=message_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            logger.info(f"Successfully sent event email for event ID {event_id}.")
        return f"Event {event_id} email sent."

    except Event.DoesNotExist:
        logger.error(f"Event with ID {event_id} does not exist.")
        return f"Event {event_id} not found."
    except Exception as exc:
        logger.error(f"Error sending email for Event ID {event_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def send_task_email(self, task_id):
    """
    Sends an email notification for a new Task.
    """
    try:
        task = Task.objects.get(id=task_id)
        # Assuming the assignee gets the email
        if not task.assignee or not task.assignee.email:
             return f"Task {task_id} has no valid assignee email."
             
        subject = f"New Task Assigned: {task.title}"
        message_body = (
            f"You have been assigned a new task: '{task.title}'\n\n"
            f"Project: {task.project.title}\n"
            f"Due Date: {task.due_date}\n"
            f"Priority: {task.priority}\n"
        )
        
        send_mail(
            subject=subject,
            message=message_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[task.assignee.email],
            fail_silently=False,
        )
        logger.info(f"Successfully sent task email for task ID {task_id}.")
        return f"Task {task_id} email sent."

    except Task.DoesNotExist:
         logger.error(f"Task with ID {task_id} does not exist.")
         return f"Task {task_id} not found."
    except Exception as exc:
        logger.error(f"Error sending email for Task ID {task_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def send_message_email(self, message_id):
    """
    Sends an email notification for an unread Message after a delay.
    """
    try:
        msg = Message.objects.get(id=message_id)
        
        # Check an idempotent condition
        if msg.is_read:
            logger.info(f"Message ID {message_id} already read. Skipping email.")
            return f"Message {message_id} read; email skipped."

        if not msg.receiver or not msg.receiver.email:
            return f"Message {message_id} has no valid receiver email."

        subject = f"New Message from {msg.sender.get_full_name() or msg.sender.username}: {msg.subject}"
        message_body = (
            f"You have a new unread message from {msg.sender.get_full_name() or msg.sender.username}.\n\n"
            f"Subject: {msg.subject}\n"
            f"Message:\n{msg.content}\n"
        )
        
        send_mail(
            subject=subject,
            message=message_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[msg.receiver.email],
            fail_silently=False,
        )
        logger.info(f"Successfully sent message email for message ID {message_id}.")
        return f"Message {message_id} email sent."

    except Message.DoesNotExist:
        logger.error(f"Message with ID {message_id} does not exist.")
        return f"Message {message_id} not found."
    except Exception as exc:
        logger.error(f"Error sending email for Message ID {message_id}: {exc}")
        raise self.retry(exc=exc)
