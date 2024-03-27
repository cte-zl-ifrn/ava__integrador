from sc4py.env import env, env_as_list, env_as_bool
import datetime

APP_VERSION = "1.1.13"

LAST_STARTUP = int(datetime.datetime.timestamp(datetime.datetime.now()) * 1000)

SHOW_USERWAY = env_as_bool("SHOW_USERWAY", True)
USERWAY_ACCOUNT = env("USERWAY_ACCOUNT", None)
SHOW_VLIBRAS = env_as_bool("SHOW_VLIBRAS", True)
SHOW_SUPPORT_FORM = env_as_bool("SHOW_SUPPORT_FORM", True)
SHOW_SUPPORT_CHAT = env_as_bool("SHOW_SUPPORT_CHAT", True)


# Apps
MY_APPS = env_as_list(
    "MY_APPS",
    [
        "middleware",
        "security",
        "health",
    ],
)
THIRD_APPS = env_as_list(
    "THIRD_APPS",
    [
        "django_extensions",
        "import_export",
        "django_json_widget",
    ],
)
DJANGO_APPS = env_as_list(
    "DJANGO_APPS",
    [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    ],
)
HACK_APPS = env_as_list("HACK_APPS", [])
INSTALLED_APPS = MY_APPS + THIRD_APPS + DJANGO_APPS + HACK_APPS
