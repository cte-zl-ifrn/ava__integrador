from django.utils.translation import gettext as _
import json
import urllib
import requests
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.utils.timezone import now
from django.http import HttpRequest, HttpResponse


def login(request: HttpRequest) -> HttpResponse:
    OAUTH = settings.OAUTH
    next = urllib.parse.quote_plus(request.GET["next"] if "next" in request.GET else "/", safe="")
    redirect_uri = f"{OAUTH['REDIRECT_URI']}?next={next}"
    redirect_uri = OAUTH["REDIRECT_URI"]
    suap_url = f"{OAUTH['BASE_URL']}/o/authorize/?response_type=code&client_id={OAUTH['CLIENTE_ID']}&redirect_uri={redirect_uri}"
    return redirect(suap_url)


def authenticate(request: HttpRequest) -> HttpResponse:
    OAUTH = settings.OAUTH

    if "code" not in request.GET:
        raise Exception(_("O código de autenticação não foi informado."))

    access_token_request_data = {
        "grant_type": "authorization_code",
        "code": request.GET.get("code"),
        "redirect_uri": OAUTH["REDIRECT_URI"],
        "client_id": OAUTH["CLIENTE_ID"],
        "client_secret": OAUTH["CLIENT_SECRET"],
    }

    request_data = json.loads(
        requests.post(
            f"{OAUTH['BASE_URL']}/o/token/",
            data=access_token_request_data,
            verify=OAUTH["VERIFY_SSL"],
        ).text
    )
    headers = {
        "Authorization": "Bearer {}".format(request_data.get("access_token")),
        "x-api-key": OAUTH["CLIENT_SECRET"],
    }
    # response_data = json.loads(requests.get(f"{OAUTH['BASE_URL']}/api/eu/", data={'scope': request_data.get('scope')}, headers=headers, verify=OAUTH['VERIFY_SSL']).text )
    response = requests.get(
        f"{OAUTH['BASE_URL']}/api/eu/?scope={request_data.get('scope')}",
        headers=headers,
        verify=OAUTH["VERIFY_SSL"],
    )
    response_data = json.loads(response.text)

    username = response_data["identificacao"]
    user = User.objects.filter(username=username).first()
    defaults = {
        "first_name": response_data.get("primeiro_nome"),
        "last_name": response_data.get("ultimo_nome"),
        "email": response_data.get("email_preferencial"),
    }

    if user is None:
        is_superuser = User.objects.count() == 0
        user = User.objects.create(
            username=username,
            is_superuser=is_superuser,
            is_staff=is_superuser,
            **defaults,
        )
    else:
        user = User.objects.filter(username=username).first()
        User.objects.filter(username=username).update(**defaults)
    auth.login(request, user)
    return redirect("admin:index")


def logout(request: HttpRequest) -> HttpResponse:
    auth.logout(request)
    return redirect("https://suap.ifrn.edu.br/accounts/logout/")
