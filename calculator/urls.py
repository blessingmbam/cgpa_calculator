from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('semester/add/', views.add_semester, name='add_semester'),
    path('semester/<int:semester_id>/', views.view_semester, name='view_semester'),
    path('semester/<int:semester_id>/delete/', views.delete_semester, name='delete_semester'),
    path('semester/<int:semester_id>/course/add/', views.add_course, name='add_course'),
    path('course/<int:course_id>/delete/', views.delete_course, name='delete_course'),
    path('settings/', views.settings_view, name='settings'),
    path('export/', views.export_page, name='export_page'),
    path('export/csv/', views.export_csv, name='export_csv'),
    
]
