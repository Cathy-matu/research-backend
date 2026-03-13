import os
import django
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import User, Founder, FounderProject

def seed_founders():
    print("Clearing old founder data (if any)...")
    FounderProject.objects.all().delete()
    Founder.objects.all().delete()

    founders_data = [
        {
            "username": "founder_a",
            "name": "Alice Smith",
            "email": "alice@example.com",
            "bio": "Tech enthusiast focusing on Ideation.",
            "projects": [
                {"name": "AI Ideation Bot", "desc": "A bot that generates ideas.", "stage": "Ideation", "offset_days": 10}
            ]
        },
        {
            "username": "founder_b",
            "name": "Bob Jones",
            "email": "bob@example.com",
            "bio": "Serial entrepreneur with an MVP.",
            "projects": [
                {"name": "Marketplace MVP", "desc": "A marketplace test.", "stage": "MVP", "offset_days": 5}
            ]
        },
        {
            "username": "founder_c",
            "name": "Charlie Brown",
            "email": "charlie@example.com",
            "bio": "Building a hardware seed project.",
            "projects": [
                {"name": "Hardware Alpha", "desc": "Seed stage hardware.", "stage": "Seed", "offset_days": 2}
            ]
        },
        {
            "username": "founder_d",
            "name": "Diana Ross",
            "email": "diana@example.com",
            "bio": "Scaling a SaaS platform.",
            "projects": [
                {"name": "Cloud SaaS", "desc": "Enterprise cloud SaaS.", "stage": "Series A", "offset_days": 0}
            ]
        }
    ]

    for data in founders_data:
        user_obj, created = User.objects.get_or_create(username=data["username"], defaults={
            "email": data["email"],
            "first_name": data["name"].split()[0],
            "last_name": data["name"].split()[-1] if len(data["name"].split()) > 1 else "",
            "role": "Research Assistant",
            "force_password_change": False
        })
        if created:
            user_obj.set_password("founder123")
            user_obj.save()

        # Update if exists
        user_obj.force_password_change = False
        user_obj.save()

        founder, f_created = Founder.objects.get_or_create(user=user_obj, defaults={
            "name": data["name"],
            "email": data["email"],
            "bio": data["bio"]
        })

        for p_data in data["projects"]:
            proj = FounderProject.objects.create(
                founder=founder,
                project_name=p_data["name"],
                description=p_data["desc"],
                stage=p_data["stage"]
            )
            proj.submission_date = timezone.now() - timedelta(days=p_data["offset_days"])
            proj.save()

    print("Successfully seeded 4 founders and their projects.")

if __name__ == "__main__":
    seed_founders()
