# Generated by Django 3.2.5 on 2021-08-20 07:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_messages', '0002_message_xml_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='invoice',
            new_name='xml',
        ),
    ]
