# models.py

from django.contrib.auth.models import User
from django.db import models
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.country}"
