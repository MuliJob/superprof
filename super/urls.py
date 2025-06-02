"""Url paths for lead app."""
from django.urls import path
from . import views


urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('success/', views.RefundSuccessView.as_view(), name='success'),
    path('superuser/list/', views.RefundListView.as_view(), name='admin_list'),
]
