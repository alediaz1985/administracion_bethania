# Generated by Django 5.0.6 on 2024-06-10 01:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Docente',
            fields=[
                ('cuil', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=255)),
                ('apellido', models.CharField(max_length=255)),
                ('fecha_nacimiento', models.DateField()),
                ('genero', models.CharField(max_length=50)),
                ('direccion', models.CharField(max_length=255)),
                ('provincia', models.CharField(max_length=100)),
                ('telefono', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('nacionalidad', models.CharField(max_length=100)),
                ('titulo_academico', models.CharField(blank=True, max_length=255, null=True)),
                ('especialidad', models.CharField(blank=True, max_length=255, null=True)),
                ('anos_experiencia', models.IntegerField(blank=True, null=True)),
                ('idiomas', models.CharField(blank=True, max_length=255, null=True)),
                ('certificaciones', models.CharField(blank=True, max_length=255, null=True)),
                ('cursos_realizados', models.CharField(blank=True, max_length=255, null=True)),
                ('fecha_ingreso', models.DateField()),
                ('numero_legajo', models.CharField(max_length=50, unique=True)),
                ('cargo', models.CharField(max_length=100)),
                ('departamento', models.CharField(max_length=100)),
                ('horario_trabajo', models.CharField(max_length=100)),
                ('salario', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('fecha_ultimo_ascenso', models.DateField(blank=True, null=True)),
                ('estado_laboral', models.CharField(blank=True, max_length=50, null=True)),
                ('contacto_emergencia', models.CharField(blank=True, max_length=255, null=True)),
                ('observaciones', models.TextField(blank=True, null=True)),
                ('cuil_supervisor', models.CharField(blank=True, max_length=20, null=True)),
                ('cursos_asignados', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'docentes',
            },
        ),
    ]
