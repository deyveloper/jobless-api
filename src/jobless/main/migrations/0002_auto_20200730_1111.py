# Generated by Django 3.0.8 on 2020-07-30 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='account',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
        ),
    ]
