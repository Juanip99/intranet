# Generated by Django 5.2.1 on 2025-05-16 16:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cartilla',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('procedencia_convenio', models.CharField(blank=True, max_length=50, null=True)),
                ('tipo_cartilla', models.CharField(blank=True, max_length=50, null=True)),
                ('matricula', models.CharField(blank=True, max_length=255, null=True)),
                ('especialidad', models.CharField(max_length=3000)),
                ('nombre', models.CharField(max_length=255)),
                ('domicilio', models.CharField(max_length=255)),
                ('telefono', models.CharField(blank=True, max_length=255, null=True)),
                ('barrio_localidad', models.CharField(blank=True, max_length=255, null=True)),
                ('provincia', models.CharField(blank=True, max_length=50, null=True)),
                ('centro_de_atencion', models.CharField(blank=True, max_length=255, null=True)),
                ('cuit', models.CharField(blank=True, max_length=15, null=True)),
                ('habilitado', models.IntegerField(default=1)),
                ('email', models.CharField(blank=True, max_length=100, null=True)),
                ('solo_derivacion', models.BooleanField(default=False)),
                ('fecha_alta', models.CharField(default='16-05-2025', max_length=15)),
                ('usuario_alta', models.IntegerField(blank=True, null=True)),
                ('fecha_baja', models.CharField(blank=True, max_length=15, null=True)),
                ('especialidades_originales', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'cartilla_online',
            },
        ),
        migrations.CreateModel(
            name='CartillaChangeRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(blank=True, choices=[('create', 'Alta'), ('update', 'Edición'), ('delete', 'Baja'), ('add_specialties', 'Agregar Especialidades')], max_length=20, null=True)),
                ('field_name', models.CharField(blank=True, max_length=255, null=True)),
                ('old_value', models.TextField(blank=True, null=True)),
                ('new_value', models.TextField(blank=True, null=True)),
                ('requested_at', models.DateTimeField(auto_now_add=True)),
                ('approved', models.BooleanField(default=False)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_changes', to=settings.AUTH_USER_MODEL)),
                ('cartilla', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='change_requests', to='cartilla.cartilla')),
                ('requested_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'cartilla_change_request',
            },
        ),
    ]
