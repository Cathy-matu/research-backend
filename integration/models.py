from django.db import models
from core.models import User

class GoogleCredentials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='google_credentials')
    token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    token_uri = models.TextField(blank=True, null=True)
    client_id = models.TextField(blank=True, null=True)
    client_secret = models.TextField(blank=True, null=True)
    scopes = models.TextField(blank=True, null=True)
    
    # Store JSON representation for easy recreation of google.oauth2.credentials.Credentials
    creds_json = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Google Credentials for {self.user.username}"
