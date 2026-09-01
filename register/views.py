from decimal import Decimal
import requests
from django.conf import settings
from django.contrib.auth import login
from django.db import transaction
from django.shortcuts import redirect, render
from .forms import RegisterForm


# conversion service over HTTP. 
# going through the REST endpoint and not importing the function directly.
# verify=False because the dev cert is self-signed 
def _convert_via_rest(c1, c2, amount):
    url = f'{settings.CONVERSION_BASE_URL}/conversion/{c1}/{c2}/{amount}'
    r = requests.get(url, verify=False, timeout=5)
    r.raise_for_status()
    return Decimal(r.json()['converted'])


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # wrap in atomic so if the conversion call dies a half-made user isnt left
            with transaction.atomic():
                user = form.save(commit=False)
                currency = form.cleaned_data['currency']
                user.currency = currency
                # everyone starts with the equivalent of £500 in their picked currency
                user.balance = _convert_via_rest('GBP', currency, 500)
                user.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'register/register.html', {'form': form})
