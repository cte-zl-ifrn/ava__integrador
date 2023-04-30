from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("portal", "0001_initial"),
        ("a4", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="usuario",
            name="campus",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="portal.campus",
                verbose_name="campus do aluno",
            ),
        ),
        migrations.AddField(
            model_name="usuario",
            name="curso",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="portal.curso",
                verbose_name="curso do aluno",
            ),
        ),
        migrations.AddField(
            model_name="usuario",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                related_name="user_set",
                related_query_name="user",
                to="auth.group",
                verbose_name="groups",
            ),
        ),
        migrations.AddField(
            model_name="usuario",
            name="polo",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="portal.polo",
                verbose_name="pólo do aluno",
            ),
        ),
        migrations.AddField(
            model_name="usuario",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="user_set",
                related_query_name="user",
                to="auth.permission",
                verbose_name="user permissions",
            ),
        ),
    ]
