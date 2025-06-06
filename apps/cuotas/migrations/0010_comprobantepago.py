# Generated by Django 5.0.6 on 2025-04-29 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuotas', '0009_alter_comprobantedrivepago_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComprobantePago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marca_temporal', models.DateTimeField()),
                ('email', models.EmailField(max_length=255)),
                ('url_comprobante', models.URLField(max_length=500)),
                ('cuil_alumno', models.CharField(max_length=20)),
                ('cuil_responsable', models.CharField(max_length=20)),
                ('ruta_local', models.CharField(blank=True, max_length=500, null=True)),
            ],
            options={
                'db_table': 'comprobantes_pago',
                'managed': False,
            },
        ),
    ]
