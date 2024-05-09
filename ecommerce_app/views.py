
from django.shortcuts import get_object_or_404, redirect, render
from .models import *
from authentication.models import *
from authentication.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import random
from django.db.models import Count
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.template.loader import render_to_string
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO


# Create your views here.

def home(request):
    try:
        products = Product.objects.annotate(total_orders=Count('orderitem')).order_by('-total_orders')[:3]
        return render(request, 'home.html', {'products': products})
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')  
    
def user_order(request):
    user_orders = Order.objects.filter(user=request.user)
    return render(request, 'my_orders.html', {'user_orders': user_orders})

def product_lists(request):
    try:
        products = Product.objects.all()
        categories = Category.objects.all()
        return render(request, 'product_list.html', {'products': products, 'categories': categories})
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('product_list') 

def product_details(request, product_id):
    try:
        product = get_object_or_404(Product, pk=product_id)
        return render(request, 'product_detail.html', {'product': product})
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')  

@login_required
def add_to_cart(request, product_id):
    try:
        product = get_object_or_404(Product, pk=product_id)
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        return redirect('product_list')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('product_list')
# -------------cart--------------------

@login_required
def view_cart(request):
    try:
        cart_items = CartItem.objects.filter(user=request.user)
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('view_cart') 

@login_required
def update_cart(request, product_id):
    try:
        if request.method == 'POST':
            quantity = int(request.POST.get('quantity'))
            cart_item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
            if quantity <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = quantity
                cart_item.save()
        return redirect('view_cart')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('view_cart')  

@login_required
def remove_from_cart(request, product_id):
    try:
        if request.method == 'POST':
            cart_item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
            cart_item.delete()
        return redirect('view_cart')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('view_cart')

@login_required
def select_address_view(request):
    try:
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
                   
                    request.session['selected_address_id'] = selected_address_id
                    return redirect('select_payment')

        return render(request, 'select_address.html', {'addresses': addresses, 'cart_items': cart_items, 'total_price': total_price})
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('view_cart')  

@login_required
def select_payment_view(request):
    try:
        selected_address_id = request.session.get('selected_address_id')
        selected_address = None
        if selected_address_id:
            selected_address = Address.objects.get(pk=selected_address_id)
            
        if request.method == 'POST':
            payment_method = request.POST.get('payment_method')
            if payment_method == 'cod':
                return place_order(request)

        return render(request, 'select_payment.html', {'selected_address': selected_address})
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('view_cart') 

@login_required
def place_order(request):
    try:
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
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('view_cart') 

def confirmation(request, invoice_number):
    try:
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
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('view_cart') 

def generate_invoice_number():
    return ''.join(random.choices('ABCDEFGHIJK0123456789', k=4))


from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa

def generate_pdf_invoice(request, invoice_number):
    try:
        order = Order.objects.get(invoice_number=invoice_number)
        order_items = OrderItem.objects.filter(order=order)

        
        context = {
            'order': order,
            'order_items': order_items,
        }
        html_string = render_to_string('invoice_template.html', context)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice_number}.pdf"'

        pisa_status = pisa.CreatePDF(html_string, dest=response)
        if pisa_status.err:
            return HttpResponse('PDF generation error: %s' % pisa_status.err)

        return response
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('view_cart')
    
    
