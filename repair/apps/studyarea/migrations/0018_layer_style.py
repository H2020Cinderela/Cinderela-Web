# Generated by Django 2.0 on 2018-03-09 16:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wms_client', '0012_remove_wmsresource_layers'),
        ('studyarea', '0017_layer_z_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='layer',
            name='style',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='wms_client.LayerStyle'),
        ),
    ]