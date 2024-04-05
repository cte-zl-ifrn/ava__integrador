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
    "REDIRECT_URI": env("OAUTH_REDIRECT_URI", "http://middleware/api/authenticate/"),
    "CLIENT_ID": env("OAUTH_CLIENT_ID", "changeme"),
    "CLIENT_SECRET": env("OAUTH_CLIENT_SECRET", "changeme"),
    "BASE_URL": env("OAUTH_BASE_URL", "http://login"),
    "VERIFY_SSL": env("OAUTH_VERIFY_SSL", False),
}
