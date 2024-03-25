import logging
import concurrent
import re
import json
import urllib.parse
import sentry_sdk
from typing import Dict, List, Union, Any
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.conf import settings
import requests
from http.client import HTTPException
from .models import Ambiente
from middleware.models import Solicitacao


CODIGO_DIARIO_REGEX = re.compile("^(\d\d\d\d\d)\.(\d*)\.(\d*)\.(.*)\.(\w*\.\d*)(#\d*)?$")
CODIGO_DIARIO_ANTIGO_ELEMENTS_COUNT = 5
CODIGO_DIARIO_NOVO_ELEMENTS_COUNT = 6
CODIGO_DIARIO_SEMESTRE_INDEX = 0
CODIGO_DIARIO_PERIODO_INDEX = 1
CODIGO_DIARIO_CURSO_INDEX = 2
CODIGO_DIARIO_TURMA_INDEX = 3
CODIGO_DIARIO_DISCIPLINA_INDEX = 4
CODIGO_DIARIO_ID_DIARIO_INDEX = 5

CODIGO_COORDENACAO_REGEX = re.compile("^(\w*)\.(\d*)(.*)*$")
CODIGO_COORDENACAO_ELEMENTS_COUNT = 3
CODIGO_COORDENACAO_CAMPUS_INDEX = 0
CODIGO_COORDENACAO_CURSO_INDEX = 1
CODIGO_COORDENACAO_SUFIXO_INDEX = 2

CODIGO_PRATICA_REGEX = re.compile("^(\d\d\d\d\d)\.(\d*)\.(\d*)\.(.*)\.(\d{11,14}\d*)$")
CODIGO_PRATICA_ELEMENTS_COUNT = 5
CODIGO_PRATICA_SUFIXO_INDEX = 4

CURSOS_CACHE = {}

CHANGE_URL = re.compile("/course/view.php\?")


def requests_get(url, headers={}, encoding="utf-8", decode=True, **kwargs):
    response = requests.get(url, headers=headers, **kwargs)

    if response.ok:
        byte_array_content = response.content
        return byte_array_content.decode(encoding) if decode and encoding is not None else byte_array_content
    else:
        exc = HTTPException("%s - %s" % (response.status_code, response.reason))
        exc.status = response.status_code
        exc.reason = response.reason
        exc.headers = response.headers
        exc.url = url
        raise exc


def get_json(url, headers={}, encoding="utf-8", json_kwargs=None, **kwargs):
    content = requests_get(url, headers=headers, encoding=encoding, **kwargs)
    return json.loads(content, **(json_kwargs or {}))


def get_json_api(ava: Ambiente, service: str, **params: dict):
    try:
        if params is not None:
            querystring = "&".join([f"{k}={v}" for k, v in params.items() if v is not None])
        else:
            querystring = ""
        url = f"{ava.base_api_url}/?{service}&{querystring}"
        content = get_json(url, headers={"Authentication": f"Token {ava.token}"})
        return content
    except Exception as e:
        logging.error(e)
        sentry_sdk.capture_exception(e)
