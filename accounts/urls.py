from django.urls import path, include
from .views import *

urlpatterns = [
    path('login/', login_page, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout_page, name='logout'),
]