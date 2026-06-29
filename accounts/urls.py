from django.urls import path
from accounts.views import * 
urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('change-pass/', change_password, name='change-pass'),
    path('profile/', profile, name='profile'),

]