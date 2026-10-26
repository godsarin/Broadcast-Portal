# Broadcast Portal - 5COSC021W Group Project

A Django web application for the Broadcast Company Engineering Department team registry.

## Project Structure

```
broadcast_portal/
├── broadcast_portal/     # Project settings, URLs
├── accounts/             # GROUP: Authentication, dashboard, profiles (all students)
├── teams/                # STUDENT 1: Team management (list, detail, members, repos, deps)
├── organisation/         # STUDENT 2: Departments, org chart, dependency map
├── messages_app/         # STUDENT 3: Internal messaging (inbox, sent, drafts, compose)
├── schedule/             # STUDENT 4: Meeting scheduler (calendar, weekly, monthly)
├── templates/            # All HTML templates
├── static/               # CSS, JS (Bootstrap loaded from CDN)
├── seed_data.py          # Sample data script
└── requirements.txt
```

## Student Allocation (Group of 4)

| Student | Module | Pages |
|---------|--------|-------|
| **Student 1** | `teams/` | Team list, team detail, add/remove members, add repos, email team |
| **Student 2** | `organisation/` | Org overview, departments, dependency map, team types |
| **Student 3** | `messages_app/` | Inbox, sent, drafts, compose, message detail, reply |
| **Student 4** | `schedule/` | Calendar view, weekly schedule, upcoming meetings, create/edit meetings |
| **ALL (Group)** | `accounts/` | Registration, login, logout, profile, dashboard, audit log |

## Setup Instructions

### 1. Install Django

```bash
pip install django>=4.2
```

### 2. Apply Migrations

```bash
cd broadcast_portal
python manage.py makemigrations
python manage.py migrate
```

### 3. Seed Sample Data

```bash
python seed_data.py
```

This creates:
- Admin user: `admin` / `admin123`
- 10 sample users (password: `password123`)
- 2 departments (Platform Engineering, Streaming & Media)
- 6 teams with 5+ members each
- Sample skills, repos, dependencies

### 4. Run the Server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

## Key URLs

| URL | Description |
|-----|-------------|
| `/accounts/login/` | Login page |
| `/accounts/register/` | Self-registration |
| `/dashboard/` | Main dashboard |
| `/teams/` | All teams (Student 1) |
| `/organisation/` | Org structure (Student 2) |
| `/organisation/departments/` | Departments (Student 2) |
| `/organisation/dependencies/` | Dependency map (Student 2) |
| `/messages/` | Inbox (Student 3) |
| `/messages/compose/` | New message (Student 3) |
| `/schedule/` | Schedule/calendar (Student 4) |
| `/schedule/meetings/create/` | New meeting (Student 4) |
| `/admin/` | Django admin panel |

## Features Implemented

### Group (Shared)
- User registration (local accounts only, no OAuth)
- Secure login/logout
- Profile management (name, email, job title, bio)
- Password change
- Audit trail for all create/update/delete operations
- Django Admin with full management capability
- Responsive Bootstrap 5 UI with sidebar navigation

### Student 1 - Teams
- Browse all teams with search (by name, department, manager)
- Filter by status (active/restructured/disbanded)
- Team detail with full info: mission, manager, contact channels
- Add/remove team members with roles
- Code repositories (GitHub/GitLab/Bitbucket etc.)
- Upstream/downstream dependencies display
- Email team (sends internal message)
- Schedule meeting directly from team page
- Team lifecycle (create, edit, disband)
- Django Admin integration

### Student 2 - Organisation
- Organisation overview with visual org chart
- Department list and detailed department pages
- Department leader, teams, specialisation
- Interactive dependency map (SVG graph with arrows)
- Team type management
- All members per department view

### Student 3 - Messages
- Inbox with unread count
- Sent messages
- Drafts (save for later)
- Compose new message
- Reply to messages
- Thread display
- Soft delete

### Student 4 - Schedule
- Monthly calendar view with colour-coded events
- Weekly meetings view
- Upcoming meetings sidebar
- Schedule meeting (date/time, platform, attendees, agenda)
- Meeting detail with join link
- Edit / cancel meetings
- Filter all meetings by status

## Technical Stack

- **Backend**: Django 4.2+, Python 3.10+
- **Database**: SQLite (db.sqlite3)
- **Frontend**: Bootstrap 5.3, Bootstrap Icons
- **JavaScript**: Vanilla JS (calendar, dependency map, org chart)
- **No external JS frameworks required**

## Admin Panel

Visit `/admin/` with `admin` / `Jake321@#`:
- Manage all users, teams, departments
- View audit log
- Add/edit meetings
- Manage messages

## Notes for Students

- Each student should work in their own Django app folder
- Shared models (User, Team, Department) are imported where needed
- The `accounts/` app is shared — coordinate on changes
- Use `python manage.py makemigrations <appname>` when changing models
- Run `python manage.py migrate` after pulling others' changes
- All views require login (`@login_required`)
- Admin-only actions check `request.user.is_staff`
