# Generated by Django 2.0 on 2018-09-27 16:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statusquo', '0008_flowtarget'),
    ]

    operations = [
        migrations.RenameField(
            model_name='flowtarget',
            old_name='objective',
            new_name='userobjective',
        ),
    ]
