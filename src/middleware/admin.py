from django.utils.translation import gettext as _
import json
from functools import update_wrapper
from django.utils.safestring import mark_safe
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils.html import format_html
from django.db import transaction
from django.urls import path, reverse
from django.contrib.admin import register, display, StackedInline
from django.db.models import JSONField
from django.forms import ModelForm
from django.contrib.admin import ModelAdmin
from django_json_widget.widgets import JSONEditorWidget
from import_export.resources import ModelResource
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget, DateTimeWidget
from .models import Ambiente, Campus, Solicitacao
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.utils import quote, unquote
from django.contrib.admin.options import IS_POPUP_VAR, TO_FIELD_VAR, flatten_fieldsets
from django.contrib.admin.helpers import AdminErrorList, AdminForm, InlineAdminFormSet
from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.core.exceptions import PermissionDenied
from import_export.admin import ImportExportMixin, ExportActionMixin
from simple_history.admin import SimpleHistoryAdmin
from safedelete.admin import SafeDeleteAdmin, SafeDeleteAdminFilter


class BaseChangeList(ChangeList):
    def url_for_result(self, result):
        pk = getattr(result, self.pk_attname)
        return reverse(
            "admin:%s_%s_view" % (self.opts.app_label, self.opts.model_name),
            args=(quote(pk),),
            current_app=self.model_admin.admin_site.name,
        )
        pk = getattr(result, self.pk_attname)
        return f"/foos/foo/{pk}/"


class BaseModelAdmin(ImportExportMixin, ExportActionMixin, SafeDeleteAdmin, SimpleHistoryAdmin):
    list_filter = [SafeDeleteAdminFilter] + list(SafeDeleteAdmin.list_filter)

    def get_changelist(self, request, **kwargs):
        return BaseChangeList

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        prefix = f"{self.opts.app_label}_{self.opts.model_name}"
        urls = [url for url in super().get_urls() if url.pattern.name is not None]
        urls.append(path("<path:object_id>/", wrap(self.preview_view), name=f"{prefix}_view"))
        return urls

    # @csrf_protect_m
    def preview_view(self, request, object_id, form_url="", extra_context=None):
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField(f"The field {to_field} cannot be referenced.")

        obj = self.get_object(request, unquote(object_id), to_field)

        if not self.has_view_or_change_permission(request, obj):
            raise PermissionDenied

        request.in_view_mode = True

        fieldsets = self.get_fieldsets(request, obj)
        ModelForm = self.get_form(request, obj, change=False, fields=flatten_fieldsets(fieldsets))
        form = ModelForm(instance=obj)
        formsets, inline_instances = self._create_formsets(request, obj, change=True)

        # form = self._get_form_for_get_fields(request, obj)
        # return [*form.base_fields, *self.get_readonly_fields(request, obj)]
        readonly_fields = [*form.base_fields, *self.get_readonly_fields(request, obj)]
        admin_form = AdminForm(form, list(fieldsets), {}, readonly_fields, model_admin=self)
        media = self.media + admin_form.media

        inline_formsets = self.get_inline_formsets(request, formsets, inline_instances, obj)
        # inline_formsets = []
        for inline_formset in inline_formsets:
            media += inline_formset.media
            inline_formset.readonly_fields = flatten_fieldsets(inline_formset.fieldsets)

        context = {
            **self.admin_site.each_context(request),
            "title": _("View %s") % self.opts.verbose_name,
            "subtitle": str(obj) if obj else None,
            "adminform": admin_form,
            "object_id": object_id,
            "original": obj,
            "is_popup": IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET,
            "to_field": to_field,
            "media": media,
            "inline_admin_formsets": inline_formsets,
            "errors": AdminErrorList(form, formsets),
            "preserved_filters": self.get_preserved_filters(request),
            "has_add_permission": True,
            "has_delete_permission": True,
            "show_delete": True,
            "change": False,
        }

        context.update(extra_context or {})

        return self.render_change_form(request, context, add=False, change=False, obj=obj, form_url=form_url)

    def get_inline_formsets(self, request, formsets, inline_instances, obj=None):
        # Edit permissions on parent model are required for editable inlines.
        if getattr(request, "in_view_mode", False):
            can_edit_parent = False
        else:
            can_edit_parent = self.has_change_permission(request, obj) if obj else self.has_add_permission(request)

        inline_admin_formsets = []
        for inline, formset in zip(inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            readonly = list(inline.get_readonly_fields(request, obj))
            if can_edit_parent:
                has_add_permission = inline.has_add_permission(request, obj)
                has_change_permission = inline.has_change_permission(request, obj)
                has_delete_permission = inline.has_delete_permission(request, obj)
            else:
                # Disable all edit-permissions, and override formset settings.
                has_add_permission = has_change_permission = has_delete_permission = False
                formset.extra = formset.max_num = 0
            has_view_permission = inline.has_view_permission(request, obj)
            prepopulated = dict(inline.get_prepopulated_fields(request, obj))
            inline_admin_formset = InlineAdminFormSet(
                inline,
                formset,
                fieldsets,
                prepopulated,
                readonly,
                model_admin=self,
                has_add_permission=has_add_permission,
                has_change_permission=has_change_permission,
                has_delete_permission=has_delete_permission,
                has_view_permission=has_view_permission,
            )
            inline_admin_formsets.append(inline_admin_formset)
        return inline_admin_formsets


DEFAULT_DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"
DEFAULT_DATETIME_FORMAT_WIDGET = DateTimeWidget(format=DEFAULT_DATETIME_FORMAT)


@register(Ambiente)
class AmbienteAdmin(BaseModelAdmin):
    class CampusInline(StackedInline):
        model = Campus
        extra = 0

    class AmbienteResource(ModelResource):
        class Meta:
            model = Ambiente
            export_order = ("nome", "url", "token", "cor_mestra", "active")
            import_id_fields = ("nome",)
            fields = export_order
            skip_unchanged = True

    list_display = ["nome", "cores", "url", "active"]
    history_list_display = list_display
    field_to_highlight = list_display[0]
    search_fields = ["nome", "url"]
    list_filter = ["active"]
    fieldsets = [
        (_("Identificação"), {"fields": ["nome", "cor_mestra"]}),
        (_("Integração"), {"fields": ["active", "url", "token"]}),
    ]
    inlines = [CampusInline]
    resource_classes = [AmbienteResource]

    @display(description="Cor")
    def cores(self, obj):
        return mark_safe(f"<span style='background: {obj.cor_mestra};'>&nbsp;&nbsp;&nbsp;</span>")


@register(Campus)
class CampusAdmin(BaseModelAdmin):
    class CampusResource(ModelResource):
        ambiente = Field(
            attribute="ambiente",
            column_name="nome_ambiente",
            widget=ForeignKeyWidget(Ambiente, field="nome"),
        )

        class Meta:
            model = Campus
            export_order = ("sigla", "descricao", "ambiente", "suap_id", "active")
            import_id_fields = ("sigla",)
            fields = export_order
            skip_unchanged = True

    list_display = ["sigla", "descricao", "ambiente", "active"]
    history_list_display = list_display
    field_to_highlight = list_display[0]
    list_filter = ["active", "ambiente"]
    search_fields = ["sigla", "descricao", "suap_id"]
    resource_classes = [CampusResource]


@register(Solicitacao)
class SolicitacaoAdmin(ModelAdmin):
    list_display = ("quando", "status_merged", "codigo_diario", "acoes", "professores")
    list_filter = ("status", "status_code")
    search_fields = ["recebido", "enviado", "respondido", "diario__codigo"]
    # autocomplete_fields = ["campus"]
    date_hierarchy = "timestamp"
    ordering = ("-timestamp",)

    class SolicitacaoAdminForm(ModelForm):
        class Meta:
            model = Solicitacao
            widgets = {"recebido": JSONEditorWidget(), "enviado": JSONEditorWidget(), "respondido": JSONEditorWidget()}
            fields = "__all__"
            readonly_fields = ["timestamp"]

    formfield_overrides = {JSONField: {"widget": JSONEditorWidget}}
    form = SolicitacaoAdminForm

    @display(description="Status")
    def status_merged(self, obj):
        return format_html(f"""{Solicitacao.Status[obj.status].display}<br>{obj.status_code}""")

    @display(description="Ações")
    def acoes(self, obj):
        return format_html(
            f"""<a class="export_link" href="{reverse("admin:middleware_solicitacao_sync", args=[obj.id])}">Reenviar</a>"""
        )

    @display(description="Campus", ordering="campus__sigla")
    def campus_sigla(self, obj):
        return obj.campus.sigla if obj.campus else "-"

    @display(description="Quando", ordering="timestamp")
    def quando(self, obj):
        return obj.timestamp.strftime("%Y-%m-%d %H:%M:%S")

    @display(description="Professores", ordering="timestamp")
    def professores(self, obj):
        try:
            recebido = json.loads(obj.recebido)
            return format_html("<ul>" + "".join([f"<li>{x['nome']}</li>" for x in recebido["professores"]]) + "</ul>")
        except Exception:
            return "-"

    @display(description="Diário", ordering="timestamp")
    def codigo_diario(self, obj):
        try:
            recebido = json.loads(obj.recebido)
            codigo = f"{recebido['turma']['codigo']}.{recebido['diario']['sigla']}#{recebido['diario']['id']}"
            try:
                respondido = json.loads(obj.respondido.replace("'", '"'))
                suap_url = "https://suap.ifrn.edu.br"
                return format_html(
                    f"""<a href='{respondido['url']}'>{codigo}</a><br>
                        <a href='{respondido['url_sala_coordenacao']}'>Coordenação</a><br>
                        <a href='{suap_url}/edu/meu_diario/{recebido['diario']['id']}/1/'>SUAP</a>"""
                )
            except Exception:
                return codigo
        except Exception:
            return "-"

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name
        return [
            path("<path:object_id>/sync_moodle/", wrap(self.sync_moodle_view), name="%s_%s_sync" % info)
        ] + super().get_urls()

    @transaction.atomic
    def sync_moodle_view(self, request, object_id, form_url="", extra_context=None):
        return None
        # s = get_object_or_404(Solicitacao, pk=object_id)
        # try:
        #     return HttpResponse(Diario.objects.sync(s.recebido))
        # except Exception as e:
        #     return HttpResponse(f"{e}")
