import os
import django
from django.utils import timezone
from datetime import date, datetime

def seed():
    from core.models import User, Project, Partner, Task, SubTask, Output, Message, Event

    # Clear existing data
    User.objects.exclude(is_superuser=True).delete()
    Project.objects.all().delete()
    Event.objects.all().delete()

    print("Seeding Users...")
    users_data = [
        {'username': 'director', 'name': 'Dr. Caroline Ayuya', 'email': 'director@drice.ac.ke', 'role': 'Director', 'avatar': 'CA'},
        {'username': 'deputy', 'name': 'Dr. Japheth Mursi', 'email': 'deputydirector@drice.ac.ke', 'role': 'Deputy Director', 'avatar': 'JM'},
        {'username': 'cathy', 'name': 'Cathy Matu', 'email': 'lead1@drice.ac.ke', 'role': 'Research Assistant', 'avatar': 'CM'},
        {'username': 'karina', 'name': 'Karina', 'email': 'lead2@drice.ac.ke', 'role': 'Research Assistant', 'avatar': 'KK'},
        {'username': 'boyani', 'name': 'Boyani', 'email': 'researcher1@drice.ac.ke', 'role': 'Research Assistant', 'avatar': 'BB'},
        {'username': 'kemunto', 'name': 'Kemunto', 'email': 'researcher2@drice.ac.ke', 'role': 'Research Assistant', 'avatar': 'KM'},
        {'username': 'faith', 'name': 'Faith K.', 'email': 'assistant@drice.ac.ke', 'role': 'Research Assistant', 'avatar': 'FK'},
        {'username': 'admin', 'name': 'System Admin', 'email': 'admin@drice.ac.ke', 'role': 'Admin', 'avatar': 'SA'},
        {'username': 'innovation', 'name': 'Innovation Lead', 'email': 'innovation@drice.ac.ke', 'role': 'Innovation Officer', 'avatar': 'IL'},
        {'username': 'analyst', 'name': 'Data Analyst', 'email': 'analyst@drice.ac.ke', 'role': 'Data Analyst', 'avatar': 'DA'},
    ]
    
    user_map = {}
    for u in users_data:
        names = u['name'].split(' ')
        first_name = names[0]
        last_name = ' '.join(names[1:]) if len(names) > 1 else ''
        user = User.objects.create_user(
            username=u['email'],
            email=u['email'],
            password='password123',
            first_name=first_name,
            last_name=last_name,
            role=u['role'],
            avatar=u['avatar']
        )
        user_map[u['username']] = user

    print("Seeding Projects...")
    projects_data = [
        {'id': 1, 'title': 'Kibera Sanitation Mapping', 'type': 'Research', 'status': 'Active', 'lead': 'deputy', 'team': ['karina', 'boyani'], 'start': '2024-01-15', 'end': '2024-12-31', 'budget': 450000, 'progress': 65},
        {'id': 2, 'title': 'AgriSmart Crop Detection', 'type': 'Pilot', 'status': 'Active', 'lead': 'cathy', 'team': ['kemunto'], 'start': '2024-03-01', 'end': '2024-09-30', 'budget': 280000, 'progress': 40},
        {'id': 3, 'title': 'Mental Health Study', 'type': 'Research', 'status': 'At Risk', 'lead': 'karina', 'team': [], 'start': '2024-02-01', 'end': '2024-08-31', 'budget': 150000, 'progress': 25},
        {'id': 4, 'title': 'AI Ethics Training', 'type': 'Training', 'status': 'Completed', 'lead': 'director', 'team': ['deputy', 'cathy', 'karina', 'boyani', 'kemunto'], 'start': '2023-09-01', 'end': '2024-01-31', 'budget': 80000, 'progress': 100},
    ]
    
    project_map = {}
    for p in projects_data:
        proj = Project.objects.create(
            id=p['id'],
            title=p['title'],
            project_type=p['type'],
            status=p['status'],
            lead=user_map[p['lead']],
            start_date=p['start'],
            end_date=p['end'],
            budget=p['budget'],
            progress=p['progress']
        )
        for member in p['team']:
            proj.team.add(user_map[member])
        project_map[p['id']] = proj

    print("Seeding Partners...")
    partners_data = [
        {'name': 'Nairobi Water Company', 'sector': 'Govt', 'contact': 'John Kimani', 'email': 'jkimani@nwc.go.ke', 'engagement': 'High', 'project_id': 1},
        {'name': 'Safaricom Foundation', 'sector': 'Industry', 'contact': 'Alice Muthoni', 'email': 'alice@safaricom.co.ke', 'engagement': 'High', 'project_id': 3},
        {'name': 'Ministry of Agriculture', 'sector': 'Govt', 'contact': 'Peter Omondi', 'email': 'pomondi@agri.go.ke', 'engagement': 'Medium', 'project_id': 2},
    ]
    for part in partners_data:
        Partner.objects.create(
            name=part['name'],
            sector=part['sector'],
            contact=part['contact'],
            email=part['email'],
            engagement=part['engagement'],
            project=project_map[part['project_id']]
        )

    print("Seeding Tasks...")
    tasks_data = [
        {'id': 1, 'project_id': 1, 'title': 'Complete field data collection', 'assignee': 'boyani', 'due': '2024-02-15', 'status': 'Done', 'priority': 'High'},
        {'id': 2, 'project_id': 1, 'title': 'GIS mapping analysis', 'assignee': 'deputy', 'due': '2024-02-28', 'status': 'In Progress', 'priority': 'High'},
        {'id': 3, 'project_id': 2, 'title': 'Train ML model v2', 'assignee': 'cathy', 'due': '2024-02-10', 'status': 'Overdue', 'priority': 'High'},
    ]
    for t in tasks_data:
        Task.objects.create(
            id=t['id'],
            project=project_map[t['project_id']],
            title=t['title'],
            assignee=user_map[t['assignee']],
            due_date=t['due'],
            status=t['status'],
            priority=t['priority']
        )

    print("Seeding Events...")
    # Based on eventSeeds.js
    events_data = [
        {
            'title': 'Hackathon for ComTech',
            'description': 'Community-driven hackathon for technology solutions in commerce',
            'start': '2026-02-17T09:00:00Z',
            'end': '2026-02-19T17:00:00Z',
            'category': 'Hackathons & Community Events',
            'stage': 'Confirmed',
            'owner': 'boyani',
            'attendees': ['director', 'deputy', 'cathy', 'karina', 'boyani', 'kemunto']
        }
    ]
    for ev in events_data:
        event = Event.objects.create(
            title=ev['title'],
            description=ev['description'],
            start_date=ev['start'],
            end_date=ev['end'],
            category=ev['category'],
            pipeline_stage=ev['stage'],
            owner=user_map[ev['owner']]
        )
        for att in ev['attendees']:
            event.attendees.add(user_map[att])

    print("\nDatabase seeded successfully!")
    print("\n" + "="*50)
    print("USER LOGIN CREDENTIALS")
    print("="*50)
    print(f"{'Role':<20} | {'Email/Username':<25} | {'Password'}")
    print("-" * 65)
    for u in users_data:
        print(f"{u['role']:<20} | {u['email']:<25} | password123")
    print("="*65 + "\n")

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    seed()
