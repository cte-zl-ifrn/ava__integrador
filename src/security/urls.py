from django.urls import path
from .apps import SecurityConfig
from .views import login, authenticate, logout


app_name = SecurityConfig.name


urlpatterns = [
    path("login/", login, name="login"),
    path("authenticate/", authenticate, name="authenticate"),
    path("logout/", logout, name="logout"),
]
