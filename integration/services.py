import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from .models import GoogleCredentials
from django.conf import settings
from datetime import datetime

class GoogleCalendarService:
    def __init__(self, user):
        """
        Initialize the service with a specific user's GoogleCredentials.
        """
        self.user = user
        self.creds = None
        
        try:
            google_creds = GoogleCredentials.objects.get(user=self.user)
            if google_creds.creds_json:
                self.creds = Credentials.from_authorized_user_info(google_creds.creds_json)
        except GoogleCredentials.DoesNotExist:
            self.creds = None

    def is_authenticated(self):
        return self.creds is not None and self.creds.valid

    def sync_event(self, event_data):
        """
        Sync a local Event model to Google Calendar.
        """
        if not self.is_authenticated():
            raise Exception(f"User {self.user.username} is not authenticated with Google Calendar.")

        service = build('calendar', 'v3', credentials=self.creds)
        
        # Prepare attendees
        attendees = []
        if event_data.attendees.exists():
            for attendee in event_data.attendees.all():
                attendees.append({'email': attendee.email})

        event_body = {
            'summary': event_data.title,
            'location': event_data.location,
            'description': event_data.description,
            'start': {
                'dateTime': event_data.start_date.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': event_data.end_date.isoformat(),
                'timeZone': 'UTC',
            },
            'attendees': attendees,
        }

        # If it already has a Google Event ID, update it. Otherwise, create new.
        if event_data.google_event_id:
            try:
                event = service.events().update(
                    calendarId='primary', 
                    eventId=event_data.google_event_id, 
                    body=event_body
                ).execute()
            except Exception as e:
                # Fallback to create if the ID is invalid or deleted remotely
                event = service.events().insert(calendarId='primary', body=event_body).execute()
        else:
            event = service.events().insert(calendarId='primary', body=event_body).execute()

        # Update the local Event record with Google's identifiers
        event_data.google_event_id = event.get('id')
        event_data.google_calendar_link = event.get('htmlLink')
        event_data.save()
        
        return event

    def delete_event(self, google_event_id):
        """
        Delete an event from Google Calendar.
        """
        if not self.is_authenticated() or not google_event_id:
            return False
            
        service = build('calendar', 'v3', credentials=self.creds)
        try:
            service.events().delete(calendarId='primary', eventId=google_event_id).execute()
            return True
        except Exception:
            return False
