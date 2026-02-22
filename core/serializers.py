from rest_framework import serializers
from .models import User, Project, Task, SubTask, Partner, Output, Message, Event

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'avatar', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ['id', 'title', 'completed']

class TaskSerializer(serializers.ModelSerializer):
    assignee_name = serializers.ReadOnlyField(source='assignee.get_full_name')
    subtasks = SubTaskSerializer(many=True, read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'project', 'title', 'assignee', 'assignee_name', 
            'due_date', 'status', 'priority', 'dependencies', 'subtasks', 'created_at'
        ]

class PartnerSerializer(serializers.ModelSerializer):
    project_title = serializers.ReadOnlyField(source='project.title')
    
    class Meta:
        model = Partner
        fields = ['id', 'name', 'sector', 'contact', 'email', 'engagement', 'project', 'project_title']

class ProjectSerializer(serializers.ModelSerializer):
    lead_name = serializers.ReadOnlyField(source='lead.get_full_name')
    team_names = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'project_type', 'status', 'lead', 'lead_name', 
            'team', 'team_names', 'start_date', 'end_date', 'budget', 'progress'
        ]

    def get_team_names(self, obj):
        return [user.get_full_name() for user in obj.team.all()]

class OutputSerializer(serializers.ModelSerializer):
    project_title = serializers.ReadOnlyField(source='project.title')
    author_names = serializers.SerializerMethodField()
    
    class Meta:
        model = Output
        fields = ['id', 'project', 'project_title', 'output_type', 'title', 'status', 'date', 'authors', 'author_names', 'frequency']

    def get_author_names(self, obj):
        return [user.get_full_name() for user in obj.authors.all()]

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.ReadOnlyField(source='sender.get_full_name')
    receiver_name = serializers.ReadOnlyField(source='receiver.get_full_name')
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_name', 'receiver', 'receiver_name', 'project', 'subject', 'content', 'timestamp', 'status', 'priority', 'parent', 'replies']

    def get_replies(self, obj):
        if obj.replies.exists():
            return MessageSerializer(obj.replies.all(), many=True).data
        return []

class EventSerializer(serializers.ModelSerializer):
    owner_name = serializers.ReadOnlyField(source='owner.get_full_name')
    attendee_details = UserSerializer(source='attendees', many=True, read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'start_date', 'end_date', 'category', 
            'pipeline_stage', 'location', 'owner', 'owner_name', 'attendees', 
            'attendee_details', 'max_attendees', 'linked_project', 'created_at'
        ]
