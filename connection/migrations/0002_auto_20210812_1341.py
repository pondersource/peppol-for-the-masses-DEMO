# Generated by Django 3.2.5 on 2021-08-12 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('connection', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='is_customer',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='contact',
            name='is_supplier',
            field=models.BooleanField(default=False),
        ),
    ]