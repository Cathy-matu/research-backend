from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Event, Task, Message
from .tasks import send_event_email, send_task_email, send_message_email

# @receiver(post_save, sender=Event)
# def event_post_save(sender, instance, created, **kwargs):
#     if created:
#         send_event_email.delay(instance.id)

# @receiver(post_save, sender=Task)
# def task_post_save(sender, instance, created, **kwargs):
#     if created:
#         send_task_email.delay(instance.id)

# @receiver(post_save, sender=Message)
# def message_post_save(sender, instance, created, **kwargs):
#     if created:
#         # the read-check delay is implemented here (60 seconds)
#         send_message_email.apply_async(kwargs={'message_id': instance.id}, countdown=60)
