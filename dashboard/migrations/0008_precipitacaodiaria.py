# Generated by Django 3.0.6 on 2020-08-14 20:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_auto_20200814_1845'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrecipitacaoDiaria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('value', models.FloatField(blank=True, max_length=100, null=True)),
                ('estacao', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.Estacao')),
            ],
        ),
    ]