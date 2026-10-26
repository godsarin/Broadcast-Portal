#!/usr/bin/env python
"""
Seed script for Broadcast Portal - creates sample data for demonstration.
Run: python seed_data.py
(from project root, with Django settings available)
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'broadcast_portal.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from organisation.models import Department, TeamType
from teams.models import Team, TeamMembership, Skill, CodeRepository


def run():
    print("🌱 Seeding Broadcast Portal database...")

    # Create superuser admin
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser('admin', 'admin@broadcast.com', 'admin123')
        UserProfile.objects.get_or_create(user=admin, defaults={'job_title': 'Platform Admin'})
        print("✅ Admin user created: username=admin, password=admin123")
    else:
        admin = User.objects.get(username='admin')

    # Create regular users
    users_data = [
    ('alice_smith', 'Alice', 'Smith', 'alice@broadcast.com', 'Senior Engineer'),
    ('bob_jones', 'Bob', 'Jones', 'bob@broadcast.com', 'Tech Lead'),
    ('carol_white', 'Carol', 'White', 'carol@broadcast.com', 'Software Engineer'),
    ('dave_brown', 'Dave', 'Brown', 'dave@broadcast.com', 'DevOps Engineer'),
    ('emma_davis', 'Emma', 'Davis', 'emma@broadcast.com', 'QA Engineer'),
    ('frank_miller', 'Frank', 'Miller', 'frank@broadcast.com', 'Software Engineer'),
    ('grace_wilson', 'Grace', 'Wilson', 'grace@broadcast.com', 'Senior Engineer'),
    ('henry_moore', 'Henry', 'Moore', 'henry@broadcast.com', 'Engineering Manager'),
    ('iris_taylor', 'Iris', 'Taylor', 'iris@broadcast.com', 'Software Engineer'),
    ('jack_anderson', 'Jack', 'Anderson', 'jack@broadcast.com', 'Tech Lead'),
  ]

    users = {}
    for username, first, last, email, title in users_data:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'first_name': first, 'last_name': last, 'email': email}
        )
        if created:
            user.set_password('password123')
            user.save()
        profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'job_title': title})
        users[username] = user
    print(f"✅ Created {len(users_data)} users (password: password123)")

    # Create team types
    TeamType.objects.get_or_create(name='Platform', defaults={'color': '#0d6efd', 'description': 'Platform infrastructure teams'})
    TeamType.objects.get_or_create(name='Product', defaults={'color': '#198754', 'description': 'Product delivery teams'})
    TeamType.objects.get_or_create(name='Enablement', defaults={'color': '#fd7e14', 'description': 'Enablement and tooling teams'})

    # Create departments
    dept1, _ = Department.objects.get_or_create(
        name='Platform Engineering',
        defaults={
            'description': 'Responsible for core infrastructure, developer tooling, and platform reliability.',
            'specialisation': 'Cloud Infrastructure, CI/CD, Developer Experience',
            'leader': users['henry_moore'],
            'email': 'platform@broadcast.com',
            'slack_channel': '#platform-eng',
        }
    )

    dept2, _ = Department.objects.get_or_create(
        name='Streaming & Media',
        defaults={
            'description': 'Delivers live and on-demand streaming services across all broadcast channels.',
            'specialisation': 'Video Encoding, CDN, Live Events',
            'leader': users['jack_anderson'],
            'email': 'streaming@broadcast.com',
            'slack_channel': '#streaming-media',
        }
    )
    print("✅ Created 2 departments")

    # Create skills
    skills = {}
    for skill_name in ['Python', 'Django', 'Kubernetes', 'Docker', 'AWS', 'React', 'PostgreSQL', 'Redis', 'Terraform', 'Go', 'Java', 'FFmpeg']:
        skill, _ = Skill.objects.get_or_create(name=skill_name)
        skills[skill_name] = skill

    # Create teams for Platform Engineering (3+ teams)
    team_data = [
        {
            'name': 'Core Infrastructure',
            'dept': dept1,
            'manager': users['henry_moore'],
            'description': 'Manages the core cloud infrastructure, networking, and reliability for all Broadcast services. Responsible for uptime SLAs.',
            'slack_channel': '#infra-core',
            'email': 'infra@broadcast.com',
            'skills': ['Kubernetes', 'Terraform', 'AWS'],
            'members': [
                (users['alice_smith'], 'senior_engineer'),
                (users['dave_brown'], 'devops'),
                (users['carol_white'], 'engineer'),
                (users['emma_davis'], 'qa'),
                (users['frank_miller'], 'engineer'),
            ]
        },
        {
            'name': 'Developer Experience',
            'dept': dept1,
            'manager': users['bob_jones'],
            'description': 'Builds and maintains internal developer tools, CI/CD pipelines, and onboarding experiences for all engineering teams.',
            'slack_channel': '#dev-experience',
            'email': 'devex@broadcast.com',
            'skills': ['Python', 'Docker', 'Django'],
            'members': [
                (users['bob_jones'], 'lead'),
                (users['grace_wilson'], 'senior_engineer'),
                (users['iris_taylor'], 'engineer'),
                (users['carol_white'], 'engineer'),
                (users['frank_miller'], 'engineer'),
            ]
        },
        {
            'name': 'Data & Analytics',
            'dept': dept1,
            'manager': users['alice_smith'],
            'description': 'Provides data pipelines, analytics dashboards, and reporting capabilities to all business units.',
            'slack_channel': '#data-analytics',
            'email': 'data@broadcast.com',
            'skills': ['Python', 'PostgreSQL', 'Redis'],
            'members': [
                (users['alice_smith'], 'lead'),
                (users['dave_brown'], 'engineer'),
                (users['emma_davis'], 'qa'),
                (users['henry_moore'], 'manager'),
                (users['iris_taylor'], 'engineer'),
            ]
        },
        # Streaming & Media dept teams
        {
            'name': 'Live Streaming',
            'dept': dept2,
            'manager': users['jack_anderson'],
            'description': 'Responsible for all live broadcast streaming, encoding pipelines, and real-time distribution to viewers worldwide.',
            'slack_channel': '#live-streaming',
            'email': 'live@broadcast.com',
            'skills': ['FFmpeg', 'Go', 'AWS'],
            'members': [
                (users['jack_anderson'], 'lead'),
                (users['grace_wilson'], 'senior_engineer'),
                (users['bob_jones'], 'engineer'),
                (users['frank_miller'], 'engineer'),
                (users['emma_davis'], 'qa'),
            ]
        },
        {
            'name': 'VOD Platform',
            'dept': dept2,
            'manager': users['grace_wilson'],
            'description': 'Manages the video-on-demand (VOD) platform including content ingestion, storage, and delivery at scale.',
            'slack_channel': '#vod-platform',
            'email': 'vod@broadcast.com',
            'skills': ['Java', 'AWS', 'React'],
            'members': [
                (users['grace_wilson'], 'lead'),
                (users['alice_smith'], 'engineer'),
                (users['carol_white'], 'senior_engineer'),
                (users['dave_brown'], 'devops'),
                (users['iris_taylor'], 'qa'),
            ]
        },
        {
            'name': 'CDN & Distribution',
            'dept': dept2,
            'manager': users['dave_brown'],
            'description': 'Operates the content delivery network and manages global distribution rules for all Broadcast digital content.',
            'slack_channel': '#cdn-distribution',
            'email': 'cdn@broadcast.com',
            'skills': ['Kubernetes', 'Go', 'Terraform'],
            'members': [
                (users['dave_brown'], 'lead'),
                (users['henry_moore'], 'engineer'),
                (users['frank_miller'], 'senior_engineer'),
                (users['jack_anderson'], 'engineer'),
                (users['emma_davis'], 'engineer'),
            ]
        },
    ]

    created_teams = {}
    for td in team_data:
        team, created = Team.objects.get_or_create(
            name=td['name'],
            defaults={
                'description': td['description'],
                'department': td['dept'],
                'manager': td['manager'],
                'slack_channel': td['slack_channel'],
                'email': td['email'],
                'status': 'active',
            }
        )
        for skill_name in td['skills']:
            team.skills.add(skills[skill_name])
        for user, role in td['members']:
            TeamMembership.objects.get_or_create(team=team, user=user, defaults={'role': role})
        # Add repos
        CodeRepository.objects.get_or_create(
            team=team, name=f"{td['name'].replace(' ', '-').lower()}-service",
            defaults={'url': f"https://github.com/broadcast/{td['name'].replace(' ', '-').lower()}", 'platform': 'github'}
        )
        created_teams[td['name']] = team

    # Set up some dependencies
    if 'Live Streaming' in created_teams and 'Core Infrastructure' in created_teams:
        created_teams['Live Streaming'].upstream_dependencies.add(created_teams['Core Infrastructure'])
    if 'VOD Platform' in created_teams and 'CDN & Distribution' in created_teams:
        created_teams['VOD Platform'].upstream_dependencies.add(created_teams['CDN & Distribution'])
    if 'CDN & Distribution' in created_teams and 'Core Infrastructure' in created_teams:
        created_teams['CDN & Distribution'].upstream_dependencies.add(created_teams['Core Infrastructure'])
    if 'Data & Analytics' in created_teams and 'Core Infrastructure' in created_teams:
        created_teams['Data & Analytics'].upstream_dependencies.add(created_teams['Core Infrastructure'])

    print(f"✅ Created {len(team_data)} teams with members, skills, repos, and dependencies")

    print("\n🎉 Database seeded successfully!")
    print("\n📋 Login credentials:")
    print("   Admin:  username=admin     password=admin123")
    print("   Users:  e.g. username=alice_smith  password=password123")
    print("   All regular users share: password=password123")
    print("\n🌐 Run the server: python manage.py runserver")
    print("   Visit: http://127.0.0.1:8000/")


if __name__ == '__main__':
    run()
