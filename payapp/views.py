from decimal import Decimal
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from register.forms import AdminCreateForm
from .forms import PayForm, RequestPaymentForm
from .models import PaymentRequest, Transaction


User = get_user_model()


# little wrapper around REST conversion endpoint. partially duplicated from
# register.views but inlining it here keeps the dependency direction tidy.
def _convert(c1, c2, amount):
    if c1 == c2:
        return Decimal(amount).quantize(Decimal('0.01'))
    url = f'{settings.CONVERSION_BASE_URL}/conversion/{c1}/{c2}/{amount}'
    r = requests.get(url, verify=False, timeout=5)
    r.raise_for_status()
    return Decimal(r.json()['converted'])


# does the actual money move + records a Transaction.
# takes both currency amounts pre-computed so accept_request can keep the requested
# amount exact in the requester's currency (one-way conversion only)
def _do_payment(sender, recipient, sender_amt, recipient_amt):
    sender_amt = Decimal(sender_amt).quantize(Decimal('0.01'))
    recipient_amt = Decimal(recipient_amt).quantize(Decimal('0.01'))

    with transaction.atomic():
        # re-fetch with select_for_update
        s = User.objects.select_for_update().get(pk=sender.pk)
        r = User.objects.select_for_update().get(pk=recipient.pk)

        if s.balance < sender_amt:
            raise ValueError('insufficient funds')

        s.balance = s.balance - sender_amt
        r.balance = r.balance + recipient_amt
        s.save(update_fields=['balance'])
        r.save(update_fields=['balance'])

        Transaction.objects.create(
            sender=s,
            recipient=r,
            amount=recipient_amt,
            currency=r.currency,
        )


# staff and superuser are treated as "admin" for this app
def _is_admin(u):
    return u.is_authenticated and u.is_staff


@login_required
def dashboard_view(request):
    user = request.user
    sent = Transaction.objects.filter(sender=user)
    received = Transaction.objects.filter(recipient=user)
    pending_requests_in = PaymentRequest.objects.filter(target=user, status='pending').count()

    return render(request, 'payapp/dashboard.html', {
        'sent': sent,
        'received': received,
        'pending_in_count': pending_requests_in,
    })


@login_required
def pay_view(request):
    if request.method == 'POST':
        form = PayForm(request.POST, sender=request.user)
        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            amount = form.cleaned_data['amount']
            # sender said amount in their currency, recipient gets the converted equivalent
            recipient_amt = _convert(request.user.currency, recipient.currency, amount)
            try:
                _do_payment(request.user, recipient, amount, recipient_amt)
                messages.success(request, f'paid {amount} {request.user.currency} to {recipient.username}')
                return redirect('dashboard')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = PayForm(sender=request.user)
    return render(request, 'payapp/pay.html', {'form': form})


@login_required
def request_payment_view(request):
    if request.method == 'POST':
        form = RequestPaymentForm(request.POST, requester=request.user)
        if form.is_valid():
            target = form.cleaned_data['target']
            amount = form.cleaned_data['amount']
            PaymentRequest.objects.create(
                requester=request.user,
                target=target,
                amount=amount,
                currency=request.user.currency,
            )
            messages.success(request, f'request sent to {target.username}')
            return redirect('dashboard')
    else:
        form = RequestPaymentForm(requester=request.user)
    return render(request, 'payapp/request.html', {'form': form})


@login_required
def notifications_view(request):
    incoming = PaymentRequest.objects.filter(target=request.user, status='pending')
    # also showing what we've sent out, makes the page more useful
    outgoing = PaymentRequest.objects.filter(requester=request.user)
    return render(request, 'payapp/notifications.html', {
        'incoming': incoming,
        'outgoing': outgoing,
    })


@login_required
def accept_request_view(request, pk):
    # POST only as accepting via GET would let people CSRF exploit
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    pr = get_object_or_404(PaymentRequest, pk=pk, target=request.user, status='pending')

    # requester wants pr.amount in their eaxact currency. target pays the
    # one-way-converted equivalent in their currency. no double conversion and no rounding gain
    sender_amt = _convert(pr.currency, request.user.currency, pr.amount)
    recipient_amt = pr.amount

    try:
        _do_payment(request.user, pr.requester, sender_amt, recipient_amt)
    except ValueError as e:
        messages.error(request, f'could not accept: {e}')
        return redirect('notifications')

    pr.status = 'accepted'
    pr.save(update_fields=['status'])
    messages.success(request, f'paid {pr.requester.username}')
    return redirect('notifications')


@login_required
def reject_request_view(request, pk):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    pr = get_object_or_404(PaymentRequest, pk=pk, target=request.user, status='pending')
    pr.status = 'rejected'
    pr.save(update_fields=['status'])
    messages.info(request, 'request rejected')
    return redirect('notifications')


@login_required
@user_passes_test(_is_admin)
def admin_users_view(request):
    users = User.objects.all().order_by('username')
    return render(request, 'payapp/admin_users.html', {'users': users})


@login_required
@user_passes_test(_is_admin)
def admin_transactions_view(request):
    txns = Transaction.objects.all()
    reqs = PaymentRequest.objects.all()
    return render(request, 'payapp/admin_transactions.html', {'txns': txns, 'reqs': reqs})


@login_required
@user_passes_test(_is_admin)
def admin_register_admin_view(request):
    if request.method == 'POST':
        form = AdminCreateForm(request.POST)
        if form.is_valid():
            new_admin = form.save(commit=False)
            new_admin.is_staff = True
            new_admin.is_superuser = True
            new_admin.currency = 'GBP'
            new_admin.balance = 0
            new_admin.save()
            messages.success(request, f'created admin {new_admin.username}')
            return redirect('admin_users')
    else:
        form = AdminCreateForm()
    return render(request, 'payapp/admin_register_admin.html', {'form': form})
