# PayApp

A PayPal style payment service built with Django. Registered users hold a balance,
send and request money in GBP, USD or EUR, and can see every transaction they were
part of. Conversion between currencies isn't done inline in the views. It sits
behind a separate REST endpoint that the payment code calls over HTTP, which keeps
the conversion logic out of the transaction flow.

## What it does

Users register with validation on the form and get an opening balance in whichever
currency they picked. Sending money means choosing a recipient and an amount in any
supported currency, and the service converts, debits and credits, then notifies the
person receiving it. Requests work the other way round: you raise one against
another user, and accepting it runs the same transfer path.

There's a transaction history showing everything a user sent or received, with the
currency each side saw. An admin role can list all users, look at every transaction
on the system, and register further administrators.

The conversion endpoint is `GET /conversion/<currency_from>/<currency_to>/<amount>/`
and returns a JSON quote. It's called from the payment code rather than from the
templates.

## Design notes

Validation lives in the form layer instead of being spread through the views.
Amounts have to be positive, the recipient has to exist, and paying yourself is
rejected before anything reaches the database.

The first administrator is created by a data migration
(`register/migrations/0002_seed_admin1.py`) rather than by a manual step, so a fresh
clone comes up with a working admin account. Templates are wired through named URL
patterns across three URLConf modules and rendered with django-crispy-forms on
Bootstrap 5.

The coursework version ran over HTTPS with a self signed certificate. The
certificate and key aren't in this repository, so generate your own if you want TLS
locally.

## Running it

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Then open http://127.0.0.1:8000/.

SECRET_KEY and DEBUG are read from the environment as DJANGO_SECRET_KEY and
DJANGO_DEBUG. If you don't set them you get a generated key and debug mode, which is
fine locally and not fine anywhere else.

## Layout

| Path | Contents |
|---|---|
| `register/` | accounts, authentication, admin registration, the seed migration |
| `payapp/` | balances, transfers, requests, notifications, admin views |
| `webservice/` | the standalone currency conversion endpoint |
| `templates/` | templates, wired through named URL patterns |

Coursework for G6060 Web Applications and Services at the University of Sussex.
MIT licensed.
