# Generated by Django 2.0.3 on 2018-04-13 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forumTopics', '0009_auto_20180413_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topics',
            name='url',
            field=models.URLField(blank=True, default=None, max_length=256, null=True),
        ),
    ]
