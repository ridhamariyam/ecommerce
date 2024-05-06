from django.shortcuts import render,redirect
from ecommerce_app.models import *
from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q

# Create your views here.
def dashboard(request):
    return render(request, 'dashboard/dashboard.html')

def order_listing(request):
    order = Order.objects.all()
    print(order,'ppppp')
    context = {
        'orders': order
    }
    return render(request, 'dashboard/order.html',context)

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

def search_and_filter_orders(request):
    query = request.GET.get('q')
    filter_option = request.GET.get('filter')
    sort_option = request.GET.get('sort')

    orders = Order.objects.all()

    if query:
        orders = orders.filter(
            Q(invoice_number__icontains=query) |
            Q(id__icontains=query) |
            Q(user__username__icontains=query)
        )

    if filter_option == 'completed':
        orders = orders.filter(status='completed')

    if sort_option == 'asc':
        orders = orders.order_by('invoice_number')
    elif sort_option == 'desc':
        orders = orders.order_by('-invoice_number')

    context = {
        'orders': orders
    }
    return render(request, 'order.html', context)