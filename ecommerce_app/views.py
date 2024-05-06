
from django.shortcuts import get_object_or_404, redirect, render
from .models import *
from authentication.models import *
from authentication.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import random


# Create your views here.

def home(request):
    return render(request, 'home.html')

def product_list(request):
    products = Product.objects.all() 
    categories = Category.objects.all() 
    return render(request, 'product_list.html', {'products': products, 'categories': categories})


def product_details(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'product_detail.html', {'product': product})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('product_list')

@login_required
def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        cart_item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()
    return redirect('view_cart')

@login_required
def remove_from_cart(request, product_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
        cart_item.delete()
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})


def select_address_view(request):
    addresses = Address.objects.filter(user=request.user)
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        street_address = request.POST.get('street_address')
        city = request.POST.get('city')
        country = request.POST.get('country')
        
        if street_address and city and country:
            existing_address = Address.objects.filter(user=request.user, street_address=street_address, city=city, country=country).first()
            if existing_address:
                messages.error(request, "Address already exists.")
            else:
                address = Address.objects.create(user=request.user, street_address=street_address, city=city, country=country)
                addresses = Address.objects.filter(user=request.user) 
                messages.success(request, "Address added successfully.")

        if 'address' in request.POST:
            selected_address_id = request.POST.get('address')
            if selected_address_id:
                # Store the selected address ID in the session
                request.session['selected_address_id'] = selected_address_id
                return redirect('select_payment')

    return render(request, 'select_address.html', {'addresses': addresses, 'cart_items': cart_items, 'total_price': total_price})

def select_payment_view(request):
    selected_address_id = request.session.get('selected_address_id')
    selected_address = None
    if selected_address_id:
        selected_address = Address.objects.get(pk=selected_address_id)
        
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        if payment_method == 'cod':
            return place_order(request)

    return render(request, 'select_payment.html', {'selected_address': selected_address})


def place_order(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    invoice_number = generate_invoice_number()
    status = 'confirmed'
    invoice_date = timezone.now().date()

    # Retrieving the selected address ID from the session
    selected_address_id = request.session.get('selected_address_id')
    selected_address = None
    if selected_address_id:
        selected_address = get_object_or_404(Address, pk=selected_address_id)
      
        request.session['selected_address'] = {
            'street_address': selected_address.street_address,
            'city': selected_address.city,
            'country': selected_address.country
        }
        
    payment_method = request.POST.get('payment_method') 

    order = Order.objects.create(user=user, 
                                 total_price=total_price, 
                                 status=status,
                                 invoice_number=invoice_number,
                                 invoice_date=invoice_date,
                                 payment_method=payment_method)  
    
  
    for item in cart_items:
        OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price_at_purchase=item.product.price)
    cart_items.delete()
    
    return redirect('confirmation', invoice_number=invoice_number)

def generate_invoice_number():
    return ''.join(random.choices('ABCDEFGHIJK0123456789', k=4))


def confirmation(request, invoice_number):
    order = Order.objects.get(invoice_number=invoice_number)
    order_items = OrderItem.objects.filter(order=order)
    
    # Retrieving the selected address information from the session
    selected_address_data = request.session.get('selected_address')
 
    selected_address = None
    if selected_address_data:
        selected_address = {
            'street_address': selected_address_data['street_address'],
            'city': selected_address_data['city'],
            'country': selected_address_data['country']
        }
    
    total_amount = order.total_price
    return render(request, 'confirmation.html', {'order_items': order_items, 'selected_address': selected_address, 'invoice_number': invoice_number, 'total_amount': total_amount})