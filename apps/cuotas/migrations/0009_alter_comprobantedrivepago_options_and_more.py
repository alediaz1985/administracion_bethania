# Generated by Django 5.0.6 on 2025-04-29 00:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cuotas', '0008_alter_comprobantedrivepago_table'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comprobantedrivepago',
            options={'verbose_name': 'Comprobantes de Pago', 'verbose_name_plural': 'Comprobantes de Pago'},
        ),
        migrations.AlterModelTable(
            name='comprobantedrivepago',
            table='comprobantes_pago',
        ),
    ]
