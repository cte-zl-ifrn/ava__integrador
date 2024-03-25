# -*- coding: utf-8 -*-
from sc4py.env import env, env_as_bool

SECRET_KEY = env("DJANGO_SECRET_KEY", "changeme")
LOGIN_URL = env("DJANGO_LOGIN_URL", "/api/login/")
LOGIN_REDIRECT_URL = env("DJANGO_LOGIN_REDIRECT_URL", "/api/admin/")
LOGOUT_REDIRECT_URL = env("DJANGO_LOGOUT_REDIRECT_URL", LOGIN_REDIRECT_URL)
GO_TO_HTTPS = env_as_bool("GO_TO_HTTPS", False)
AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)
# AUTH_USER_MODEL = env("DJANGO_AUTH_USER_MODEL", "auth.User")

# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = []

OAUTH = {
    "REDIRECT_URI": env("SUAP_OAUTH_REDIRECT_URI", "http://middleware/api/authenticate/"),
    "CLIENTE_ID": env("SUAP_OAUTH_CLIENT_ID", "changeme on docker-compose.yml"),
    "CLIENT_SECRET": env("SUAP_OAUTH_CLIENT_SECRET", "changeme on docker-compose.yml"),
    "BASE_URL": env("SUAP_OAUTH_BASE_URL", "https://suap.ifrn.edu.br"),
    "VERIFY_SSL": env("SUAP_OAUTH_VERIFY_SSL", False),
}
