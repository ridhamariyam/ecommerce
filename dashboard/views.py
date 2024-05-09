from django.shortcuts import render,redirect
from ecommerce_app.models import *
from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
import csv
from django.shortcuts import render
from django.http import HttpResponse
from .tasks import generate_order_report
from django.core.mail import EmailMessage
from io import StringIO
from authentication.models import Address
from django.contrib import messages


# Create your views here.
def dashboard(request):
    return render(request, 'dashboard/dashboard.html')


def product_listing(request):
    categories = Category.objects.all() 
    products = Product.objects.all()
    context = {
        'products': products,
        'categories': categories
    }
    return render(request, 'dashboard/products.html', context)


def order_listing(request):
    search_query = request.GET.get('q')
    if search_query:
        orders = Order.objects.filter(
            Q(invoice_number__icontains=search_query) | 
            Q(user__username__icontains=search_query)
        )
    else:   
        orders = Order.objects.all()
    
 
    if not orders.exists() and search_query:
        orders = Order.objects.all()
    
    context = {
        'orders': orders
    }
    return render(request, 'dashboard/order.html', context)


def update_order_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        order = get_object_or_404(Order, pk=order_id)
        order.status = new_status
        order.save()
        return JsonResponse({'message': 'Status updated successfully'})
    else:
     
        return redirect(reverse('order'))
    

def get_order_details(request, order_id):
    try:
        order = Order.objects.prefetch_related('orderitem_set__product').get(pk=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

    order_data = {
        'user': order.user.username,
        'total_price': order.total_price,
        'payment_method': order.payment_method,
        'items': [{
            'name': item.product.title,
            'quantity': item.quantity,
            'price': item.price_at_purchase,
            'image': item.product.image.url  
        } for item in order.orderitem_set.all()]
    }
    return JsonResponse(order_data)




def export_order_report(request):
    email_address = request.GET.get('email')

    if not email_address:
        return JsonResponse({'error': 'No email address provided.'}, status=400)

    orders = Order.objects.all()
    header = ['Invoice Number', 'User', 'Total Price', 'Status', 'Created At', 'Payment Method', 'Invoice Date']

    with StringIO() as buffer:
        writer = csv.writer(buffer)
        writer.writerow(header)
        for order in orders:
            row = [
                order.invoice_number,
                order.user.username if order.user else "",
                order.total_price,
                order.status,
                order.created_at,
                order.payment_method,
                order.invoice_date
            ]
            writer.writerow(row)

        email = EmailMessage(
            subject='Order Report',
            body='Please find attached the order report.',
            to=[email_address],
        )

        # Attaching the CSV file to the email
        email.attach('order_report.csv', buffer.getvalue(), 'text/csv')
        email.send()

        # Returning a JSON response indicating success
        response_data = {'success': True}

        # Creating an HTTP response to serve the CSV file as a download
        csv_response = HttpResponse(buffer.getvalue(), content_type='text/csv')
        csv_response['Content-Disposition'] = 'attachment; filename="order_report.csv"'

        return JsonResponse(response_data)
    
    
def users_list(request):
 
    users_with_addresses = Address.objects.select_related('user').all()
    
    context = {
        'users': users_with_addresses
    }
    return render(request, 'dashboard/user_list.html', context)

def add_product(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price')
        quantity_available = request.POST.get('quantity_available')
        category_id = request.POST.get('category_id')
        image = request.FILES.get('image')

        product = Product.objects.create(
            title=title,
            description=description,
            price=price,
            quantity_available=quantity_available,
            category_id=category_id,
            image=image
        )
       
        messages.success(request, 'Product added successfully!')

   
        return redirect('dash_products')

    return render(request, 'dashboard/products.html')