from django.urls import path
from . import views

urlpatterns = [
    path('', views.schedule_home, name='schedule_home'),
    path('meetings/', views.my_meetings, name='my_meetings'),
    path('meetings/create/', views.meeting_create, name='meeting_create'),
    path('meetings/<int:pk>/', views.meeting_detail, name='meeting_detail'),
    path('meetings/<int:pk>/edit/', views.meeting_edit, name='meeting_edit'),
    path('meetings/<int:pk>/cancel/', views.meeting_cancel, name='meeting_cancel'),
    path('meetings/<int:pk>/delete/', views.meeting_delete, name='meeting_delete'),
]
