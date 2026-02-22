from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    # Named constants for the three primary spec roles
    DIRECTOR = 'Director'
    DEPUTY_DIRECTOR = 'Deputy Director'
    RESEARCH_ASSISTANT = 'Research Assistant'

    ROLES = (
        ('Director', 'Director'),
        ('Deputy Director', 'Deputy Director'),
        ('Research Assistant', 'Research Assistant'),
        ('Admin', 'Admin'),
        ('Innovation Officer', 'Innovation Officer'),
        ('Data Analyst', 'Data Analyst'),
    )
    role = models.CharField(max_length=50, choices=ROLES, default='Research Assistant')
    avatar = models.CharField(max_length=2, blank=True)  # Initials as seen in frontend
    force_password_change = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['role']),
        ]

class Project(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('At Risk', 'At Risk'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
    )
    TYPE_CHOICES = (
        ('Research', 'Research'),
        ('Pilot', 'Pilot'),
        ('Training', 'Training'),
        ('Innovation', 'Innovation'),
    )
    title = models.CharField(max_length=255)
    project_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    lead = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='led_projects')
    team = models.ManyToManyField(User, related_name='projects')
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    progress = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['project_type']),
        ]

    def __str__(self):
        return self.title

class Partner(models.Model):
    SECTOR_CHOICES = (
        ('Govt', 'Government'),
        ('Industry', 'Industry'),
        ('NGO', 'NGO'),
        ('Academic', 'Academic'),
    )
    ENGAGEMENT_CHOICES = (
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    )
    name = models.CharField(max_length=255)
    sector = models.CharField(max_length=50, choices=SECTOR_CHOICES)
    contact = models.CharField(max_length=255)
    email = models.EmailField()
    engagement = models.CharField(max_length=20, choices=ENGAGEMENT_CHOICES)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='partners')

    class Meta:
        indexes = [
            models.Index(fields=['engagement']),
        ]

class Task(models.Model):
    STATUS_CHOICES = (
        ('To Do', 'To Do'),
        ('In Progress', 'In Progress'),
        ('Done', 'Done'),
        ('Overdue', 'Overdue'),
    )
    PRIORITY_CHOICES = (
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
        ('Urgent', 'Urgent'),
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='To Do')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    dependencies = models.ManyToManyField('self', symmetrical=False, blank=True)
    # subtasks and timeLogs can be complex; using JSONField for initial simplicity in this case
    # or separate models if performance on subtask queries is needed.
    # Given "least amount of time", models allow indexing and prefetching.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['due_date']),
        ]

class SubTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)

class Output(models.Model):
    TYPE_CHOICES = (
        ('Paper', 'Paper'),
        ('Dataset', 'Dataset'),
        ('Prototype', 'Prototype'),
        ('Report', 'Report'),
    )
    STATUS_CHOICES = (
        ('Published', 'Published'),
        ('Approved', 'Approved'),
        ('Draft', 'Draft'),
        ('Under Review', 'Under Review'),
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='outputs')
    output_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    date = models.DateField()
    authors = models.ManyToManyField(User, related_name='outputs')
    frequency = models.CharField(max_length=50, blank=True) # e.g. Monthly, Weekly
    resource_url = models.URLField(max_length=500, blank=True, null=True)
    resource_type = models.CharField(max_length=50, blank=True, null=True) # e.g. Model, Paper, Dataset, Prototype

    class Meta:
        indexes = [
            models.Index(fields=['output_type']),
            models.Index(fields=['status']),
        ]

class Message(models.Model):
    PRIORITY_CHOICES = (
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('replied', 'Replied'),
        ('archived', 'Archived'),
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=255)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['sender']),
            models.Index(fields=['receiver']),
        ]

class Event(models.Model):
    PIPELINE_STAGES = (
        ('Planning', 'Planning'),
        ('Confirmed', 'Confirmed'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    category = models.CharField(max_length=100)
    pipeline_stage = models.CharField(max_length=20, choices=PIPELINE_STAGES, default='Planning')
    location = models.CharField(max_length=255, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_events')
    attendees = models.ManyToManyField(User, related_name='attending_events')
    max_attendees = models.IntegerField(null=True, blank=True)
    linked_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    google_event_id = models.CharField(max_length=255, blank=True, null=True)
    google_calendar_link = models.URLField(max_length=500, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['start_date']),
            models.Index(fields=['pipeline_stage']),
        ]
