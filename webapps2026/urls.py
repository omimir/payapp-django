from django.http import HttpResponseRedirect
from django.urls import include, path
from webservice.views import conversion


urlpatterns = [
    # bounce to webapps2026 so the project root isn't 404
    path('', lambda r: HttpResponseRedirect('/webapps2026/')),

    # auth (register, login, logout)
    path('webapps2026/', include('register.urls')),

    # everything else for normal users + admin pages
    path('webapps2026/', include('payapp.urls')),

    # REST conversion service. 
    path('conversion/<str:currency1>/<str:currency2>/<str:amount>', conversion, name='conversion'),
]
