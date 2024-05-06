from django.urls import path
from .views import *

urlpatterns = [
    
    path('dashboard/', dashboard, name='dashboard'),
    path('order/', order_listing, name='order'),
    path('update_status/', update_order_status, name='update_status'),
    path('get_order_details/<int:order_id>/', get_order_details, name='get_order_details'),

]
