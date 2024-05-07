import csv
from io import StringIO
from celery import shared_task
from ecommerce_app.models import Order
from django.core.mail import EmailMessage

@shared_task
def generate_order_report():
    orders = Order.objects.all()
    header = ['Invoice Number', 'User', 'Total Price', 'Status', 'Created At', 'Payment Method', 'Invoice Date']

    with StringIO() as buffer:
        writer = csv.writer(buffer)
        writer.writerow(header)
        for order in orders:
            row = [
                order.invoice_number,
                order.user.username,
                order.total_price,
                order.status,
                order.created_at,
                order.payment_method,
                order.invoice_date
            ]
            writer.writerow(row)

        # Save the CSV file
        with open('order_report.csv', 'w') as file:
            file.write(buffer.getvalue())
    
       

