from django.urls import path
from . import views

"""
URL patterns for the Teams module.
All views require login (@login_required decorator applied in views.py).

Author: Sarin Pradhan (Student 1)

URL Summary:
  /teams/                                    → team_list      (browse & search all teams)
  /teams/create/                             → team_create    (admin only)
  /teams/<pk>/                               → team_detail    (full team profile)
  /teams/<pk>/edit/                          → team_edit      (staff or team manager)
  /teams/<pk>/delete/                        → team_delete    (admin only, soft-delete)
  /teams/<pk>/add-member/                    → team_add_member
  /teams/<pk>/remove-member/<membership_id>/ → team_remove_member
  /teams/<pk>/add-repo/                      → team_add_repo
  /teams/<pk>/email/                         → email_team     (sends to messages_app)
"""

urlpatterns = [
    path('', views.team_list, name='team_list'),
    path('create/', views.team_create, name='team_create'),
    path('<int:pk>/', views.team_detail, name='team_detail'),
    path('<int:pk>/edit/', views.team_edit, name='team_edit'),
    path('<int:pk>/delete/', views.team_delete, name='team_delete'),
    path('<int:pk>/add-member/', views.team_add_member, name='team_add_member'),
    path('<int:pk>/remove-member/<int:membership_id>/', views.team_remove_member, name='team_remove_member'),
    path('<int:pk>/add-repo/', views.team_add_repo, name='team_add_repo'),
    path('<int:pk>/email/', views.email_team, name='email_team'),
]
