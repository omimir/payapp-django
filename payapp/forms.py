from decimal import Decimal
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


# pay form lets you find the recipient by either username or email.
# little bit nicer than forcing one or the other.
class PayForm(forms.Form):
    recipient = forms.CharField(label='recipient (username or email)', max_length=150)
    amount = forms.DecimalField(min_value=Decimal('0.01'), max_digits=12, decimal_places=2)

    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)

    def clean_recipient(self):
        val = self.cleaned_data['recipient'].strip()
        # try username first, fall back to email
        try:
            user = User.objects.get(username=val)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=val)
            except User.DoesNotExist:
                raise forms.ValidationError("no user with that username or email")
        if self.sender and user.pk == self.sender.pk:
            raise forms.ValidationError("can't pay yourself")
        return user

    def clean(self):
        cleaned = super().clean()
        amt = cleaned.get('amount')
        if self.sender and amt is not None and amt > self.sender.balance:
            raise forms.ValidationError(
                f"not enough funds (you have {self.sender.balance} {self.sender.currency})"
            )
        return cleaned


# request form, same idea but no balance check
class RequestPaymentForm(forms.Form):
    target = forms.CharField(label='who to ask (username or email)', max_length=150)
    amount = forms.DecimalField(min_value=Decimal('0.01'), max_digits=12, decimal_places=2)

    def __init__(self, *args, **kwargs):
        self.requester = kwargs.pop('requester', None)
        super().__init__(*args, **kwargs)

    def clean_target(self):
        val = self.cleaned_data['target'].strip()
        try:
            user = User.objects.get(username=val)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=val)
            except User.DoesNotExist:
                raise forms.ValidationError("no user with that username or email")
        if self.requester and user.pk == self.requester.pk:
            raise forms.ValidationError("can't request from yourself")
        return user
