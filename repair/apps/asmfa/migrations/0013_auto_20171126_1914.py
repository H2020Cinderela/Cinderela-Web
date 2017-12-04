# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-26 19:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('asmfa', '0012_auto_20171126_1743'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='keyflow',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='asmfa.KeyflowInCasestudy'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activity2activity',
            name='keyflow',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='asmfa.KeyflowInCasestudy'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activity2activity',
            name='product',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ActivityFlows', to='asmfa.Product'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activity2activity',
            name='quality',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='asmfa.Quality'),
        ),
        migrations.AddField(
            model_name='activitygroup',
            name='keyflow',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='asmfa.KeyflowInCasestudy'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activitystock',
            name='keyflow',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='asmfa.KeyflowInCasestudy'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activitystock',
            name='product',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ActivityStocks', to='asmfa.Product'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='actor',
            name='keyflow',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='asmfa.KeyflowInCasestudy'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='actor2actor',
            name='keyflow',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='asmfa.KeyflowInCasestudy'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='actor2actor',
            name='product',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ActorFlows', to='asmfa.Product'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='actor2actor',
            name='quality',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='asmfa.Quality'),
        ),
        migrations.AddField(
            model_name='actorstock',
            name='keyflow',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='asmfa.KeyflowInCasestudy'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='actorstock',
            name='product',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ActorStocks', to='asmfa.Product'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='group2group',
            name='keyflow',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='asmfa.KeyflowInCasestudy'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='group2group',
            name='product',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='GroupFlows', to='asmfa.Product'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='group2group',
            name='quality',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='asmfa.Quality'),
        ),
        migrations.AddField(
            model_name='groupstock',
            name='keyflow',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='asmfa.KeyflowInCasestudy'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='groupstock',
            name='product',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='GroupStocks', to='asmfa.Product'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='keyflow',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='asmfa.KeyflowInCasestudy'),
            preserve_default=False,
        ),
    ]