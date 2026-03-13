from django.test import TestCase, override_settings
from django.core import mail
from django.utils import timezone
from .models import User, Project, Event, Task, Message

@override_settings(CELERY_TASK_ALWAYS_EAGER=True, EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EmailNotificationTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='director', email='director@test.com', role='Director')
        self.user2 = User.objects.create_user(username='assistant', email='assistant@test.com', role='Research Assistant')
        self.project = Project.objects.create(
            title='Test Project', 
            project_type='Research',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=30),
            budget=10000.00,
            lead=self.user1
        )

    def test_event_creation_sends_email(self):
        self.assertEqual(len(mail.outbox), 0)
        Event.objects.create(
            title='Strategy Meeting',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(hours=1),
            owner=self.user1
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('New Event: Strategy Meeting', mail.outbox[0].subject)

    def test_task_creation_sends_email(self):
        self.assertEqual(len(mail.outbox), 0)
        Task.objects.create(
            title='Write Report',
            project=self.project,
            assignee=self.user2,
            due_date=timezone.now().date()
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('New Task Assigned: Write Report', mail.outbox[0].subject)

    def test_unread_message_sends_email(self):
        self.assertEqual(len(mail.outbox), 0)
        # Message created as unread by default
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            subject='Urgent Update',
            content='Please review the document.'
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('New Message from director', mail.outbox[0].subject)

    def test_read_message_skips_email(self):
        self.assertEqual(len(mail.outbox), 0)
        
        # We need a way to mock the 60 second delay and message read state
        # In CELERY_TASK_ALWAYS_EAGER=True, the task executes immediately upon saving.
        # This makes it tricky to simulate "user reads message within 60 seconds", 
        # so we'll construct the instance with is_read=True prior to save to verify the task logic skips it. (Or mock it within tests).
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            subject='FYI',
            content='Already read this.',
            is_read=True
        )
        self.assertEqual(len(mail.outbox), 0)
