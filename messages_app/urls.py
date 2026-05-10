from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('sent/', views.sent_messages, name='sent_messages'),
    path('drafts/', views.drafts, name='drafts'),
    path('compose/', views.compose, name='compose'),
    path('compose/<int:recipient_id>/', views.compose, name='compose_to'),
    path('reply/<int:reply_to>/', views.compose, name='reply'),
    path('<int:pk>/', views.message_detail, name='message_detail'),
    path('<int:pk>/send-draft/', views.send_draft, name='send_draft'),
    path('<int:pk>/delete/', views.delete_message, name='delete_message'),
]
