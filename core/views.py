from rest_framework import viewsets, permissions, generics, status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User, Project, Task, Partner, Output, Message, Event
from .serializers import (
    UserSerializer, ProjectSerializer, TaskSerializer, 
    PartnerSerializer, OutputSerializer, MessageSerializer, EventSerializer
)
from .permissions import IsDirectorOrDeputy, IsAdmin, IsOwnerOrStaff
from .reports import ReportGenerator
from integration.services import MicrosoftGraphService

class UserMeView(generics.RetrieveAPIView):
    """Returns the profile and role of the currently authenticated user."""
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [permissions.IsAuthenticated(), IsAdmin()]

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.select_related('lead').prefetch_related('team').all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsDirectorOrDeputy | IsAdmin]

    @action(detail=True, methods=['get'])
    def generate_report(self, request, pk=None):
        report_data = ReportGenerator.generate_weekly_summary(pk)
        if report_data:
            return Response(report_data)
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related('assignee', 'project').prefetch_related('subtasks', 'dependencies').all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff | IsDirectorOrDeputy | IsAdmin]

class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.select_related('project').all()
    serializer_class = PartnerSerializer
    permission_classes = [permissions.IsAuthenticated]

class OutputViewSet(viewsets.ModelViewSet):
    queryset = Output.objects.select_related('project').prefetch_related('authors').all()
    serializer_class = OutputSerializer
    permission_classes = [permissions.IsAuthenticated]

from django.db.models import Q

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.select_related('sender', 'receiver', 'project').prefetch_related('replies').all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]
    
    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().filter(Q(sender=user) | Q(receiver=user))

    @action(detail=True, methods=['post'])
    def send_to_outlook(self, request, pk=None):
        message = self.get_object()
        ms_graph = MicrosoftGraphService()
        try:
            ms_graph.send_email(
                subject=f"Leadership Query: {message.subject}",
                body=message.content,
                recipient_email=message.receiver.email
            )
            return Response({'status': 'Email sent successfully via Outlook'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.select_related('owner', 'linked_project').prefetch_related('attendees').all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
