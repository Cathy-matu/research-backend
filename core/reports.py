from django.utils import timezone
from datetime import timedelta
from .models import Project, Task, Output

class ReportGenerator:
    @staticmethod
    def generate_weekly_summary(project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return None

        last_week = timezone.now() - timedelta(days=7)
        
        # Aggregate tasks completed in the last week
        completed_tasks = project.tasks.filter(
            status='Done'
        )
        
        # Aggregate pending/overdue tasks
        pending_tasks = project.tasks.filter(status__in=['To Do', 'In Progress', 'Overdue'])
        
        # Aggregate new outputs
        new_outputs = project.outputs.filter(date__gte=last_week)
        
        report_data = {
            'project_title': project.title,
            'report_date': timezone.now().date(),
            'progress': project.progress,
            'completed_tasks_count': completed_tasks.count(),
            'pending_tasks': [t.title for t in pending_tasks],
            'new_outputs': [o.title for o in new_outputs],
            'status': project.status
        }
        
        return report_data
