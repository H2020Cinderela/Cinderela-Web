# Generated by Django 2.0 on 2018-07-17 15:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('asmfa', '0029_auto_20180503_1411'),
        ('studyarea', '0021_auto_20180717_1133'),
    ]

    operations = [
        migrations.CreateModel(
            name='District',
            fields=[
                ('area_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='studyarea.Area')),
            ],
            options={
                'abstract': False,
                'default_permissions': ('add', 'change', 'delete', 'view'),
            },
            bases=('studyarea.area',),
        ),
        migrations.CreateModel(
            name='Municipality',
            fields=[
                ('area_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='studyarea.Area')),
                ('parent_area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='municipality_areas', to='studyarea.Area')),
            ],
            options={
                'abstract': False,
                'default_permissions': ('add', 'change', 'delete', 'view'),
            },
            bases=('studyarea.area',),
        ),
        migrations.RemoveField(
            model_name='lau1',
            name='area_ptr',
        ),
        migrations.RemoveField(
            model_name='lau1',
            name='parent_area',
        ),
        migrations.RemoveField(
            model_name='lau2',
            name='area_ptr',
        ),
        migrations.RemoveField(
            model_name='lau2',
            name='parent_area',
        ),
        migrations.DeleteModel(
            name='LAU1',
        ),
        migrations.DeleteModel(
            name='LAU2',
        ),
        migrations.AddField(
            model_name='district',
            name='parent_area',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='district_areas', to='studyarea.Area'),
        ),
    ]
