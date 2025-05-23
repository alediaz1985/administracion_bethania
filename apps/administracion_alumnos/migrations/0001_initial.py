# Generated by Django 5.0.6 on 2024-12-06 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Estudiante',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('marca_temporal', models.CharField(max_length=100)),
                ('email_registro', models.CharField(max_length=100)),
                ('foto_estudiante', models.CharField(max_length=100)),
                ('salita_grado_anio_estudiante', models.CharField(max_length=100)),
                ('nivel_estudiante', models.CharField(max_length=100)),
                ('num_legajo_estudiante', models.CharField(max_length=100)),
                ('fecha_recepcion', models.CharField(max_length=100)),
                ('apellidos_estudiante', models.CharField(max_length=100)),
                ('nombres_estudiante', models.CharField(max_length=100)),
                ('sexo_estudiante', models.CharField(max_length=100)),
                ('fecha_nac_estudiante', models.CharField(max_length=100)),
                ('nacionalidad_estudiante', models.CharField(max_length=100)),
                ('ciudad_estudiante', models.CharField(max_length=100)),
                ('calle_estudiante', models.CharField(max_length=100)),
                ('n_mz_pc_estudiante', models.CharField(max_length=100)),
                ('barrio_estudiante', models.CharField(max_length=100)),
                ('codigo_postal_estudiante', models.CharField(max_length=100)),
                ('provincia_estudiante', models.CharField(max_length=100)),
                ('cuil_estudiante', models.CharField(max_length=100)),
                ('dni_estudiante', models.CharField(max_length=100)),
                ('email_estudiante', models.CharField(max_length=100)),
                ('religion_estudiante', models.CharField(max_length=100)),
                ('tel_fijo_estudiante', models.CharField(max_length=100)),
                ('tel_cel_estudiante', models.CharField(max_length=100)),
                ('tel_emergencia_estudiante', models.CharField(max_length=100)),
                ('parentesco_estudiante', models.CharField(max_length=100)),
                ('peso_estudiante', models.CharField(max_length=100)),
                ('talla_estudiante', models.CharField(max_length=100)),
                ('obra_social_estudiante', models.CharField(max_length=100)),
                ('cual_osocial_estudiante', models.CharField(max_length=100)),
                ('problema_neurologico_estudiante', models.CharField(max_length=100)),
                ('cual_prob_neurologico_estudiante', models.CharField(max_length=100)),
                ('problema_fisico_estudiante', models.CharField(max_length=100)),
                ('certificado_medico_estudiante', models.CharField(max_length=100)),
                ('problema_aprendizaje_estudiante', models.CharField(max_length=100)),
                ('cual_aprendizaje_estudiante', models.CharField(max_length=100)),
                ('atencion_medica_estudiante', models.CharField(max_length=100)),
                ('alergia_estudiante', models.CharField(max_length=100)),
                ('dni_responsable1', models.CharField(max_length=100)),
                ('apellidos_responsable1', models.CharField(max_length=100)),
                ('nombres_responsable1', models.CharField(max_length=100)),
                ('nacionalidad_responsable1', models.CharField(max_length=100)),
                ('fecha_nac_responsable1', models.CharField(max_length=100)),
                ('estado_civil_responsable1', models.CharField(max_length=100)),
                ('cuil_responsable1', models.CharField(max_length=100)),
                ('nivel_instruccion_responsable1', models.CharField(max_length=100)),
                ('calle_responsable1', models.CharField(max_length=100)),
                ('n_mz_pc_responsable1', models.CharField(max_length=100)),
                ('barrio_responsable1', models.CharField(max_length=100)),
                ('ciudad_responsable1', models.CharField(max_length=100)),
                ('codigo_postal_responsable1', models.CharField(max_length=100)),
                ('provincia_responsable1', models.CharField(max_length=100)),
                ('email_responsable1', models.CharField(max_length=100)),
                ('religion_responsable1', models.CharField(max_length=100)),
                ('tel_fijo_responsable1', models.CharField(max_length=100)),
                ('tel_cel_responsable1', models.CharField(max_length=100)),
                ('ocupacion_responsable1', models.CharField(max_length=100)),
                ('tel_laboral_responsable1', models.CharField(max_length=100)),
                ('horario_trab_responsable1', models.CharField(max_length=100)),
                ('dni_responsable2', models.CharField(max_length=100)),
                ('apellidos_responsable2', models.CharField(max_length=100)),
                ('nombres_responsable2', models.CharField(max_length=100)),
                ('nacionalidad_responsable2', models.CharField(max_length=100)),
                ('fecha_nac_responsable2', models.CharField(max_length=100)),
                ('estado_civil_responsable2', models.CharField(max_length=100)),
                ('cuil_responsable2', models.CharField(max_length=100)),
                ('nivel_instruccion_responsable2', models.CharField(max_length=100)),
                ('calle_responsable2', models.CharField(max_length=100)),
                ('n_mz_pc_responsable2', models.CharField(max_length=100)),
                ('barrio_responsable2', models.CharField(max_length=100)),
                ('ciudad_responsable2', models.CharField(max_length=100)),
                ('codigo_postal_responsable2', models.CharField(max_length=100)),
                ('provincia_responsable2', models.CharField(max_length=100)),
                ('email_responsable2', models.CharField(max_length=100)),
                ('religion_responsable2', models.CharField(max_length=100)),
                ('tel_fijo_responsable2', models.CharField(max_length=100)),
                ('tel_cel_responsable2', models.CharField(max_length=100)),
                ('ocupacion_responsable2', models.CharField(max_length=100)),
                ('tel_laboral_responsable2', models.CharField(max_length=100)),
                ('horario_trab_responsable2', models.CharField(max_length=100)),
                ('dni_responsable_otro', models.CharField(max_length=100)),
                ('apellidos_responsable_otro', models.CharField(max_length=100)),
                ('nombres_responsable_otro', models.CharField(max_length=100)),
                ('nacionalidad_responsable_otro', models.CharField(max_length=100)),
                ('fecha_nac_responsable_otro', models.CharField(max_length=100)),
                ('estado_civil_responsable_otro', models.CharField(max_length=100)),
                ('cuil_responsable_otro', models.CharField(max_length=100)),
                ('nivel_instruccion_responsable_otro', models.CharField(max_length=100)),
                ('calle_responsable_otro', models.CharField(max_length=100)),
                ('n_mz_pc_responsable_otro', models.CharField(max_length=100)),
                ('barrio_responsable_otro', models.CharField(max_length=100)),
                ('ciudad_responsable_otro', models.CharField(max_length=100)),
                ('codigo_postal_responsable_otro', models.CharField(max_length=100)),
                ('provincia_responsable_otro', models.CharField(max_length=100)),
                ('email_responsable_otro', models.CharField(max_length=100)),
                ('religion_responsable_otro', models.CharField(max_length=100)),
                ('tel_fijo_responsable_otro', models.CharField(max_length=100)),
                ('tel_cel_responsable_otro', models.CharField(max_length=100)),
                ('ocupacion_responsable_otro', models.CharField(max_length=100)),
                ('tel_laboral_responsable_otro', models.CharField(max_length=100)),
                ('horario_trab_responsable_otro', models.CharField(max_length=100)),
                ('anio_cursado', models.CharField(max_length=100)),
                ('donde_cursado', models.CharField(max_length=100)),
                ('asignaturas_pendientes', models.CharField(max_length=100)),
                ('indica_asig_pendientes', models.CharField(max_length=100)),
                ('tiene_hermanos_institucion', models.CharField(max_length=100)),
                ('cuantos_hermanos', models.CharField(max_length=100)),
                ('nivel_inicial3', models.CharField(max_length=100)),
                ('nivel_inicial4', models.CharField(max_length=100)),
                ('nivel_inicial5', models.CharField(max_length=100)),
                ('nivel_primario1', models.CharField(max_length=100)),
                ('nivel_primario2', models.CharField(max_length=100)),
                ('nivel_primario3', models.CharField(max_length=100)),
                ('nivel_primario4', models.CharField(max_length=100)),
                ('nivel_primario5', models.CharField(max_length=100)),
                ('nivel_primario6', models.CharField(max_length=100)),
                ('nivel_primario7', models.CharField(max_length=100)),
                ('nivel_secundario1', models.CharField(max_length=100)),
                ('nivel_secundario2', models.CharField(max_length=100)),
                ('nivel_secundario3', models.CharField(max_length=100)),
                ('nivel_secundario4', models.CharField(max_length=100)),
                ('nivel_secundario5', models.CharField(max_length=100)),
                ('como_conociste_institucion', models.CharField(max_length=100)),
                ('eligio_institucion', models.CharField(max_length=100)),
                ('nivel_ensenanza', models.CharField(max_length=100)),
                ('ciudad_a_los_dias', models.CharField(max_length=100)),
                ('senores1', models.CharField(max_length=100)),
                ('dni_senores1', models.CharField(max_length=100)),
                ('senores2', models.CharField(max_length=100)),
                ('dni_senores2', models.CharField(max_length=100)),
                ('domicilios_senores', models.CharField(max_length=100)),
                ('domicilio_especial_electronico', models.CharField(max_length=100)),
                ('actuan_nombres_estudiante', models.CharField(max_length=100)),
                ('dni_acutan_estudiante', models.CharField(max_length=100)),
                ('domicilio_actuan_estudiante', models.CharField(max_length=100)),
                ('responsable_pago', models.CharField(max_length=100)),
                ('dni_responsable_pago', models.CharField(max_length=100)),
                ('manifiesta_responsable', models.CharField(max_length=100)),
                ('autoriza_facturacion', models.CharField(max_length=100)),
                ('autoriza_imagen', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'estudiante',
            },
        ),
    ]
