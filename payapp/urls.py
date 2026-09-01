from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('pay/', views.pay_view, name='pay'),
    path('request/', views.request_payment_view, name='request_payment'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:pk>/accept/', views.accept_request_view, name='accept_request'),
    path('notifications/<int:pk>/reject/', views.reject_request_view, name='reject_request'),

    # admin pages
    path('admin-page/users/', views.admin_users_view, name='admin_users'),
    path('admin-page/transactions/', views.admin_transactions_view, name='admin_transactions'),
    path('admin-page/register-admin/', views.admin_register_admin_view, name='admin_register_admin'),
]
