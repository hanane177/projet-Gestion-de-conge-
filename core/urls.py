from django.urls import path
from . import views
from .views import  employee_dashboard, hr_dashboard, admin_dashboard, CustomLoginView, custom_logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView






urlpatterns = [
    path('', views.home, name='accueil'),
    path('about/', views.about, name='about'),  # About page
    path('service/', views.service, name='service'),  # Service page
    path('contact/', views.contact, name='contact'),  # Contact page
    path('contact/submit/', views.contact_view, name='submit_contact_form'),
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.create_user, name='create_user'),
    path('users/<int:user_id>/edit/', views.update_user, name='update_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('employee-dashboard/', employee_dashboard, name='employee_dashboard'),
    path('hr-dashboard/', hr_dashboard, name='hr_dashboard'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('data-security/', views.data_security, name='data_security'),
    path('login/', CustomLoginView.as_view(), name='login'),
    # Route pour la déconnexion
    path('accounts/logout/', custom_logout, name='logout'),
    path('profile/', views.view_profile, name='view_profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('redirect_dashboard/', views.redirect_dashboard, name='redirect_dashboard'),



]