from django.contrib.auth.models import AbstractUser
from django.db import models


# extending AbstractUser to get currency + balance on every user.
class CustomUser(AbstractUser):
    CURRENCY_CHOICES = [
        ('GBP', 'GBP'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
    ]

    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='GBP')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.username} ({self.currency} {self.balance})'
