from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('products/', product_list, name='product_list'),
    path('products/<int:product_id>/', product_details, name='product_detail'),
    path('cart/', view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
     path('select-address/', select_address_view, name='select_address'),
     path('select-payment/', select_payment_view, name='select_payment'),
     path('place_order/', place_order, name='place_order'),
    path('confirmation/<str:invoice_number>/',confirmation, name='confirmation'),
    # path('checkout/', checkout, name='checkout'),
]
