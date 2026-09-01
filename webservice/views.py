from decimal import Decimal, InvalidOperation
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseNotFound, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt


# hardcoded rates 
# values are roughly current as of when this was written
RATES = {
    ('GBP', 'USD'): Decimal('1.27'),
    ('GBP', 'EUR'): Decimal('1.17'),
    ('USD', 'GBP'): Decimal('0.79'),
    ('EUR', 'GBP'): Decimal('0.85'),
    ('USD', 'EUR'): Decimal('0.92'),
    ('EUR', 'USD'): Decimal('1.09'),
}

SUPPORTED = {'GBP', 'USD', 'EUR'}


# csrf_exempt, this is a public read-only endpoint 
# from CSRF before 405 fires
@csrf_exempt
def conversion(request, currency1, currency2, amount):
    # GET only, else returns 405
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    c1 = currency1.upper()
    c2 = currency2.upper()

    # 404 if either currency isn't one supported
    if c1 not in SUPPORTED or c2 not in SUPPORTED:
        return HttpResponseNotFound('unsupported currency')

    # parse amount could come in as "100" or "100.5"
    try:
        amt = Decimal(amount)
    except InvalidOperation:
        return HttpResponseBadRequest('amount must be a number')

    if c1 == c2:
        # same currency
        converted = amt
    else:
        rate = RATES[(c1, c2)]
        converted = (amt * rate).quantize(Decimal('0.01'))

    return JsonResponse({
        'currency1': c1,
        'currency2': c2,
        'amount': str(amt),
        'converted': str(converted),
    })
