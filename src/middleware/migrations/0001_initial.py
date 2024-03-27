# Generated by Django 5.0.3 on 2024-03-26 14:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Ambiente",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "cor_mestra",
                    models.CharField(
                        help_text="Escolha uma cor em RGB.\n                Ex.: <span style='background: #a04ed0; color: #fff; padding: 1px 5px; font-size: 95%; border-radius: 4px;'>#a04ed0</span> <span style='background: #396ba7; color: #fff; padding: 1px 5px; font-size: 95%; border-radius: 4px;'>#396ba7</span> <span style='background: #559c1a; color: #fff; padding: 1px 5px; font-size: 95%; border-radius: 4px;'>#559c1a</span> <span style='background: #fabd57; color: #fff; padding: 1px 5px; font-size: 95%; border-radius: 4px;'>#fabd57</span> <span style='background: #fd7941; color: #fff; padding: 1px 5px; font-size: 95%; border-radius: 4px;'>#fd7941</span> <span style='background: #f54f3b; color: #fff; padding: 1px 5px; font-size: 95%; border-radius: 4px;'>#f54f3b</span> <span style='background: #2dcfe0; color: #fff; padding: 1px 5px; font-size: 95%; border-radius: 4px;'>#2dcfe0</span>",
                        max_length=255,
                        verbose_name="cor mestra",
                    ),
                ),
                (
                    "nome",
                    models.CharField(max_length=255, verbose_name="nome do ambiente"),
                ),
                ("url", models.CharField(max_length=255, verbose_name="URL")),
                ("token", models.CharField(max_length=255, verbose_name="token")),
                ("active", models.BooleanField(default=True, verbose_name="ativo?")),
            ],
            options={
                "verbose_name": "ambiente",
                "verbose_name_plural": "ambientes",
                "ordering": ["nome"],
            },
        ),
        migrations.CreateModel(
            name="Campus",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "suap_id",
                    models.CharField(
                        max_length=255, unique=True, verbose_name="ID do campus no SUAP"
                    ),
                ),
                (
                    "sigla",
                    models.CharField(
                        max_length=255, unique=True, verbose_name="sigla do campus"
                    ),
                ),
                (
                    "descricao",
                    models.CharField(max_length=255, verbose_name="descrição"),
                ),
                ("active", models.BooleanField(verbose_name="ativo?")),
                (
                    "ambiente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="middleware.ambiente",
                    ),
                ),
            ],
            options={
                "verbose_name": "campus",
                "verbose_name_plural": "campi",
                "ordering": ["sigla"],
            },
        ),
        migrations.CreateModel(
            name="Solicitacao",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "timestamp",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="quando ocorreu"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("S", "Sucesso"),
                            ("F", "Falha"),
                            ("P", "Processando"),
                        ],
                        max_length=256,
                        null=True,
                        verbose_name="status",
                    ),
                ),
                (
                    "status_code",
                    models.CharField(
                        blank=True,
                        max_length=256,
                        null=True,
                        verbose_name="status code",
                    ),
                ),
                (
                    "recebido",
                    models.JSONField(
                        blank=True, null=True, verbose_name="JSON recebido"
                    ),
                ),
                (
                    "enviado",
                    models.JSONField(
                        blank=True, null=True, verbose_name="JSON enviado"
                    ),
                ),
                (
                    "respondido",
                    models.JSONField(
                        blank=True, null=True, verbose_name="JSON respondido"
                    ),
                ),
                (
                    "campus",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="middleware.campus",
                    ),
                ),
            ],
            options={
                "verbose_name": "solicitação",
                "verbose_name_plural": "solicitações",
                "ordering": ["-timestamp"],
            },
        ),
    ]
