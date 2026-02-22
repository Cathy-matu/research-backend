from rest_framework import viewsets, permissions, generics, status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User, Project, Task, Partner, Output, Message, Event
from .serializers import (
    UserSerializer, ProjectSerializer, TaskSerializer, 
    PartnerSerializer, OutputSerializer, MessageSerializer, EventSerializer, ChangePasswordSerializer
)
from .permissions import IsDirectorOrDeputy, IsAdmin, IsOwnerOrStaff
from .reports import ReportGenerator
from integration.services import GoogleCalendarService

class UserMeView(generics.RetrieveAPIView):
    """Returns the profile and role of the currently authenticated user."""
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class ChangePasswordView(generics.UpdateAPIView):
    """Allows an authenticated user to change their password and disable the force flag."""
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdmin()]
        return [permissions.IsAuthenticated()]

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Project.objects.select_related('lead').prefetch_related('team').all()
        if user.role in ['Admin', 'Director', 'Deputy Director', 'Innovation Officer']:
            return queryset
        return queryset.filter(Q(lead=user) | Q(team=user)).distinct()

    @action(detail=True, methods=['get'])
    def generate_report(self, request, pk=None):
        report_data = ReportGenerator.generate_weekly_summary(pk)
        if report_data:
            return Response(report_data)
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.select_related('assignee', 'project').prefetch_related('subtasks', 'dependencies').all()
        if user.role in ['Admin', 'Director', 'Deputy Director', 'Innovation Officer']:
            return queryset
        return queryset.filter(Q(assignee=user) | Q(project__lead=user) | Q(project__team=user)).distinct()

class PartnerViewSet(viewsets.ModelViewSet):
    serializer_class = PartnerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Partner.objects.select_related('project').all()
        if user.role in ['Admin', 'Director', 'Deputy Director', 'Innovation Officer']:
            return queryset
        return queryset.filter(Q(project__lead=user) | Q(project__team=user)).distinct()

class OutputViewSet(viewsets.ModelViewSet):
    serializer_class = OutputSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Output.objects.select_related('project').prefetch_related('authors').all()
        if user.role in ['Admin', 'Director', 'Deputy Director', 'Innovation Officer']:
            return queryset
        return queryset.filter(Q(authors=user) | Q(project__lead=user) | Q(project__team=user)).distinct()

from django.db.models import Q

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Message.objects.select_related('sender', 'receiver', 'project').prefetch_related('replies').filter(Q(sender=user) | Q(receiver=user)).distinct()

    @action(detail=True, methods=['post'])
    def send_to_email(self, request, pk=None):
        return Response({'status': 'Email forwarding via Google is not yet implemented.'}, status=status.HTTP_501_NOT_IMPLEMENTED)

class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Event.objects.select_related('owner', 'linked_project').prefetch_related('attendees').all()
        if user.role in ['Admin', 'Director', 'Deputy Director', 'Innovation Officer']:
            return queryset
        return queryset.filter(Q(owner=user) | Q(attendees=user) | Q(linked_project__lead=user) | Q(linked_project__team=user)).distinct()

    def _sync_to_google(self, event):
        service = GoogleCalendarService(event.owner)
        if service.is_authenticated():
            try:
                service.sync_event(event)
            except Exception as e:
                # Log error but allow local save to succeed so we don't block the UI
                print(f"Failed to sync to Google Calendar: {e}")

    def perform_create(self, serializer):
        event = serializer.save()
        self._sync_to_google(event)

    def perform_update(self, serializer):
        event = serializer.save()
        self._sync_to_google(event)

    def perform_destroy(self, instance):
        service = GoogleCalendarService(instance.owner)
        if getattr(instance, 'google_event_id', None) and service.is_authenticated():
            try:
                service.delete_event(instance.google_event_id)
            except Exception as e:
                print(f"Failed to delete from Google Calendar: {e}")
        instance.delete()
