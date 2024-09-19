# conge/urls.py
from django.urls import path
from . import views
from .views import leave_list, leave_detail
from .views import add_department
from .views import leave_type_list
from .views import submit_leave
from .views import request_status
from .views import request_history
from .views import delete_leave_request
from .views import list_departments
from .views import get_leave_events



urlpatterns = [
    path('', views.submit_leave, name='submit_leave'),
    path('success/', views.leave_success, name='leave_success'),  
    path('leave-list/', views.leave_list, name='leave_list'),
    path('conge/detail/<int:pk>/', leave_detail, name='leave_detail'),
    path('leave/<int:id>/validate/', views.valider_demande, name='valider_demande'),
    path('leave/<int:id>/reject/', views.rejeter_demande, name='rejeter_demande'),
    path('leave-calendar/', views.leave_calendar, name='leave_calendar'),
    path('add-department/', views.add_department, name='add_department'),
    path('generate-reports/', views.generate_reports, name='generate_reports'),
    path('leave_balance/', views.leave_balance, name='leave_balance'),
    path('list/', leave_type_list, name='leave_type_list'),
    path('submit-leave/', submit_leave, name='submit_leave'),
    path('request_status/', request_status, name='request_status'),
    path('request_history/', request_history, name='request_history'),
    path('manage-religious-holidays/', views.manage_religious_holidays, name='manage_religious_holidays'),
    path('add-religious-holiday/', views.add_religious_holiday, name='add_religious_holiday'),
    path('edit-religious-holiday/<int:pk>/', views.edit_religious_holiday, name='edit_religious_holiday'),
    path('delete-religious-holiday/<int:pk>/', views.delete_religious_holiday, name='delete_religious_holiday'),
    path('leave-request/<int:pk>/delete/', delete_leave_request, name='delete_leave_request'),
    path('generate_pdf/<int:pk>/', views.generate_pdf, name='generate_pdf'),
    path('liste-departements/', list_departments, name='list_departments'),
    path('api/leave-events/', get_leave_events, name='get_leave_events'),

]
