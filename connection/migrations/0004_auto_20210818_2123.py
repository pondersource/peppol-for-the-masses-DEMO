# Generated by Django 3.2.5 on 2021-08-18 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('connection', '0003_auto_20210817_1143'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='is_costumer',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='contact',
            name='is_supplier',
            field=models.BooleanField(default=False),
        ),
    ]