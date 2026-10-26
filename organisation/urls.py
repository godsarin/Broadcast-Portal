from django.urls import path
from . import views

urlpatterns = [
    path('', views.organisation_overview, name='organisation_overview'),
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/', views.department_detail, name='department_detail'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
    path('team-types/', views.teamtype_list, name='teamtype_list'),
    path('team-types/create/', views.teamtype_create, name='teamtype_create'),
    path('dependencies/', views.dependency_map, name='dependency_map'),
]
