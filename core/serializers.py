from rest_framework import serializers
from .models import User, Project, Task, SubTask, Partner, Output, Message, Event, Innovator, Idea, Founder, FounderProject

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'avatar', 'password', 'force_password_change']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        role = self.initial_data.get('role')
        if role == 'Founder' and not value.endswith('@daystar.ac.ke'):
            raise serializers.ValidationError("Use your @daystar.ac.ke email.")
        elif role != 'Founder' and not value.endswith('@drice.ac.ke'):
            raise serializers.ValidationError("Use your @drice.ac.ke email.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.force_password_change = False
        instance.save()
        return instance

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
        fields = ['id', 'name', 'sector', 'contact', 'email', 'phone', 'engagement', 'project', 'project_title']

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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.user.role in ['Research Assistant', 'Data Analyst']:
            representation.pop('budget', None)
        return representation

class OutputSerializer(serializers.ModelSerializer):
    project_title = serializers.ReadOnlyField(source='project.title')
    author_names = serializers.SerializerMethodField()
    
    class Meta:
        model = Output
        fields = ['id', 'project', 'project_title', 'output_type', 'title', 'status', 'date', 'authors', 'author_names', 'frequency', 'resource_url', 'resource_type']

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

class InnovatorSerializer(serializers.ModelSerializer):
    idea_title = serializers.ReadOnlyField(source='idea.project_title')

    class Meta:
        model = Innovator
        fields = ['id', 'name', 'year', 'email', 'idea', 'idea_title', 'created_at']

class IdeaSerializer(serializers.ModelSerializer):
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), source='project', required=False, allow_null=True
    )
    
    class Meta:
        model = Idea
        fields = ['id', 'owner_name', 'project_title', 'email', 'phone', 'project', 'project_id', 'projects_desc', 'created_at']
        extra_kwargs = {'project': {'read_only': True}}


class FounderProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = FounderProject
        fields = ['id', 'project_name', 'description', 'submission_date', 'stage']


class FounderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    projects = FounderProjectSerializer(many=True, read_only=True)

    class Meta:
        model = Founder
        fields = ['id', 'user', 'name', 'email', 'bio', 'projects', 'created_at']


class InnovationOfficerFounderSummarySerializer(serializers.ModelSerializer):
    project_title = serializers.SerializerMethodField()
    stage = serializers.SerializerMethodField()

    class Meta:
        model = Founder
        fields = ['id', 'name', 'email', 'bio', 'project_title', 'stage']

    def get_project_title(self, obj):
        project = obj.projects.first()
        return project.project_name if project else None

    def get_stage(self, obj):
        project = obj.projects.first()
        return project.stage if project else None

