from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='account-login-page'),
    path('login/', views.account_login, name='user_account-login-function'),
    path('create_admin_user/', views.create_admin_user, name='create_admin_user'),
    
]