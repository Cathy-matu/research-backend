import os
import json
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from google_auth_oauthlib.flow import Flow
from .models import GoogleCredentials

# Define the scopes required for our app
SCOPES = [
    'https://www.googleapis.com/auth/calendar.events',
]

def get_google_oauth_flow(state=None):
    """
    Helper function to configure the Google OAuth2 flow based on .env credentials.
    In a real-world scenario with a client_secret.json, you'd use InstalledAppFlow.
    Since we only have the raw Client ID and Secret in .env, we construct it manually.
    """
    client_config = {
        "web": {
            "client_id": os.getenv('GOOGLE_CLIENT_ID'),
            "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    
    flow = Flow.from_client_config(
        client_config, 
        scopes=SCOPES, 
        state=state
    )
    
    # Needs to perfectly match the Authorized redirect URIs in Google Cloud Console
    flow.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/api/v1/integration/google/callback/')
    return flow

class GoogleLoginView(APIView):
    """
    Initiates the Google OAuth2 login flow.
    The user must be authenticated so we can attach the Google token to their account later.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        flow = get_google_oauth_flow()
        
        # We enforce "offline" access to receive a refresh token so we can sync in the background
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent' # Forces Google to always return a refresh_token
        )
        
        # Store state and the user ID in the session or a cache to verify upon callback
        request.session['google_oauth_state'] = state
        request.session['google_oauth_user_id'] = request.user.id
        
        # Return the URL for the frontend to redirect the user
        return Response({'authorization_url': authorization_url})

class GoogleCallbackView(APIView):
    """
    Handles the redirect from Google, exchanges the code for tokens, 
    and saves them in the GoogleCredentials model.
    """
    # Exclude IsAuthenticated here because the redirect from Google doesn't have the Bearer token
    permission_classes = [] 

    def get(self, request):
        state = request.GET.get('state')
        code = request.GET.get('code')
        error = request.GET.get('error')

        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        # Retrieve the user ID that initiated this flow
        user_id = request.session.get('google_oauth_user_id')
        session_state = request.session.get('google_oauth_state')

        if not user_id or state != session_state:
            return Response({'error': 'State mismatch or session expired.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            flow = get_google_oauth_flow(state=state)
            
            # Use the full internal URL Django received to fetch the token
            authorization_response = request.build_absolute_uri()
            # If deploying behind a proxy (like Vercel), force https matching
            if 'vercel.app' in authorization_response:
                authorization_response = authorization_response.replace('http:', 'https:')

            flow.fetch_token(authorization_response=authorization_response)
            credentials = flow.credentials

            # Save the credentials to the database for this user
            from core.models import User
            user = User.objects.get(id=user_id)

            google_creds, created = GoogleCredentials.objects.get_or_create(user=user)
            google_creds.token = credentials.token
            google_creds.refresh_token = credentials.refresh_token
            google_creds.token_uri = credentials.token_uri
            google_creds.client_id = credentials.client_id
            google_creds.client_secret = credentials.client_secret
            google_creds.scopes = ','.join(credentials.scopes) if credentials.scopes else ''
            
            # Serialize full credentials to JSON logic for easy recreation in building calendar services later
            google_creds.creds_json = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            
            google_creds.save()

            # Clean up session
            del request.session['google_oauth_state']
            del request.session['google_oauth_user_id']
            
        
            frontend_url = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')[0]
            return redirect(f"{frontend_url}/dashboard?google_calendar_connected=true")

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
