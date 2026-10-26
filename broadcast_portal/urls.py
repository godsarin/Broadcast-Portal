from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('teams/', include('teams.urls')),
    path('organisation/', include('organisation.urls')),
    path('messages/', include('messages_app.urls')),
    path('schedule/', include('schedule.urls')),
    path('dashboard/', include('accounts.urls_dashboard')),
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
]
