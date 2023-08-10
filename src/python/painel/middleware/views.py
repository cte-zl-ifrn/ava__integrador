import json
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.http import HttpRequest, JsonResponse
from django.conf import settings
from sentry_sdk import capture_exception
from painel.models import Diario
from painel.managers import SyncError
from middleware.models import Solicitacao
from painel import request2dict


def response_error(request: HttpRequest, error: Exception):
    event_id = capture_exception(error)
    error_json = {
        "error": getattr(error, "message", None),
        "code": getattr(error, "code", 500),
        "event_id": event_id,
    }

    return JsonResponse(error_json, status=getattr(error, "code", 500))


@csrf_exempt
@transaction.atomic
def moodle_suap(request: HttpRequest):
    try:
        if not hasattr(settings, "SUAP_EAD_KEY"):
            raise SyncError("Você se esqueceu de configurar a settings 'SUAP_EAD_KEY'.", 428)

        if "HTTP_AUTHENTICATION" not in request.META:
            raise SyncError("Envie o token de autenticação no header.", 431)

        if f"Token {settings.SUAP_EAD_KEY}" != request.META["HTTP_AUTHENTICATION"]:
            raise SyncError(
                "Você enviou um token de auteticação diferente do que tem na settings 'SUAP_EAD_KEY'.",  # noqa
                403,
            )

        if request.method != "POST":
            raise SyncError("Não implementado.", 501)

        try:
            message_string = request.body.decode("utf-8")
        except Exception as e1:
            return SyncError(f"Erro ao decodificar o body em utf-8 ({e1}).", 405)

        try:
            json.dumps(message_string)
        except Exception as e1:
            return SyncError(f"Erro ao converter para JSON ({e1}).", 407)

        response = Diario.objects.sync(message_string)
        return JsonResponse(response, safe=False)
    except SyncError as se:
        return response_error(request, se)
    except Exception as e2:
        return response_error(request, e2)
