from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


# subclassing UserCreationForm gives username + password1 + password2 + the
# password validators for free.
class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    currency = forms.ChoiceField(choices=CustomUser.CURRENCY_CHOICES)

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'currency', 'password1', 'password2')


# tiny form for creating another admin from the admin pages.
# using UserCreationForm again for the password handling
class AdminCreateForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
