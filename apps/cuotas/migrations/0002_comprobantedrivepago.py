# Generated by Django 5.0.6 on 2024-12-12 03:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuotas', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComprobanteDrivePago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marca_temporal', models.CharField(max_length=150, verbose_name='Marca Temporal')),
                ('correo_electronico', models.CharField(max_length=150, verbose_name='Dirección de Correo Electrónico')),
                ('comprobante_pago', models.CharField(max_length=150, verbose_name='Adjunte el Comprobante de Pagos')),
                ('cuil_alumno', models.CharField(max_length=50, verbose_name='CUIL del Alumno')),
                ('cuil_responsable_pago', models.CharField(max_length=50, verbose_name='CUIL del Responsable de Pago')),
            ],
            options={
                'verbose_name': 'Comprobante de Pago',
                'verbose_name_plural': 'Comprobantes de Pago',
            },
        ),
    ]
