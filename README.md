# Django E-commerce Application

This Django-based E-commerce application provides core functionalities for managing products, user authentication, shopping cart, orders, and dashboard views for administrators. It allows customers to browse products, add them to the cart, manage cart items, and complete orders. Administrators can view orders, generate invoices, and export order reports.

## Features

- **User Authentication**: Users can register, log in, and log out. Authentication is required for accessing certain functionalities like managing the shopping cart and completing orders.

- **Product Management**: Admins can add, update, and delete products. Each product contains information such as title, description, price, quantity available, image, and category.

- **Shopping Cart**: Customers can add products to their shopping cart, update quantities, and remove items.

- **Order Processing**: Users can complete orders by providing necessary information such as shipping address and payment details.

- **Dashboard Views**: Administrators can view a list of orders, individual order details, generate invoices, and export order reports.

- **Invoice Generation**: Invoices are generated automatically for completed orders and saved as PDF files.

- **Order Report Export**: Order reports can be exported in CSV format using Celery for asynchronous task execution.

## Technologies Used

- Django
- SQLite3
- Celery

## Installation
   ```bash
   -git clone <repository-url>
   -cd ecommerce_project
   -pip install -r requirements.txt
   -python manage.py migrate
   -python manage.py runserver

 **Access the application at http://localhost:8000**

