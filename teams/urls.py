from django.urls import path
from . import views

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
