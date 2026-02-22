import os
from O365 import Account, MSGraphProtocol
from django.conf import settings
from datetime import datetime

class MicrosoftGraphService:
    def __init__(self):
        self.client_id = os.getenv('MS_GRAPH_CLIENT_ID')
        self.client_secret = os.getenv('MS_GRAPH_CLIENT_SECRET')
        self.tenant_id = os.getenv('MS_GRAPH_TENANT_ID')
        
        self.credentials = (self.client_id, self.client_secret)
        self.protocol = MSGraphProtocol()
        self.account = Account(self.credentials, tenant_id=self.tenant_id, protocol=self.protocol)

    def authenticate(self):
        """
        Handle OAuth2 authentication. 
        In a production environment, this would involve redirecting the user.
        For backend-to-backend (daemon) integration, we use client credentials.
        """
        if not self.account.is_authenticated:
            # This is a simplified version for common research use-cases
            # In a real app, you'd store tokens in a database per user
            return self.account.authenticate(scopes=['https://graph.microsoft.com/.default'])
        return True

    def sync_event(self, event_data):
        """
        Sync a local Event model to Outlook.
        """
        schedule = self.account.schedule()
        calendar = schedule.get_default_calendar()
        
        new_event = calendar.new_event()
        new_event.subject = event_data.title
        new_event.location = event_data.location
        new_event.body = event_data.description
        new_event.start = event_data.start_date
        new_event.end = event_data.end_date
        
        if event_data.attendees.exists():
            for attendee in event_data.attendees.all():
                new_event.attendees.add(attendee.email)
        
        new_event.save()
        return new_event.ical_uid

    def send_email(self, subject, body, recipient_email):
        """
        Send an email via Outlook (e.g., for "Ask Team Lead" fallback).
        """
        m = self.account.new_message()
        m.to.add(recipient_email)
        m.subject = subject
        m.body = body
        return m.send()

    def get_messages(self, limit=10):
        """
        Retrieve recent messages (for syncing back or checking responses).
        """
        mailbox = self.account.mailbox()
        messages = mailbox.get_messages(limit=limit)
        return messages
