from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    
   
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
]
