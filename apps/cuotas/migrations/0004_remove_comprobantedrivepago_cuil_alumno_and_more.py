# Generated by Django 5.0.6 on 2024-12-12 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuotas', '0003_alter_comprobantedrivepago_table'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comprobantedrivepago',
            name='cuil_alumno',
        ),
        migrations.AddField(
            model_name='comprobantedrivepago',
            name='cuil_estudiante',
            field=models.CharField(default=11111111, max_length=50, verbose_name='CUIL del Estudiante'),
            preserve_default=False,
        ),
    ]
