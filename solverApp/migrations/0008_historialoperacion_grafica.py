# Generated by Django 5.2.2 on 2025-06-23 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solverApp', '0007_historialoperacion_iteraciones_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historialoperacion',
            name='grafica',
            field=models.TextField(blank=True, null=True),
        ),
    ]
