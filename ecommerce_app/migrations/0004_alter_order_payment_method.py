# Generated by Django 5.0.4 on 2024-05-05 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce_app', '0003_order_payment_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('Credit Card', 'Credit Card'), ('PayPal', 'PayPal'), ('Cod', 'cod')], max_length=20),
        ),
    ]