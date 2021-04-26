# Generated by Django 2.0.2 on 2018-03-10 04:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forumTopics', '0002_auto_20180202_0446'),
    ]

    operations = [
        migrations.CreateModel(
            name='Еmployees',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lastName', models.CharField(default=None, max_length=64, verbose_name='Фамилия')),
                ('firstName', models.CharField(default=None, max_length=64, verbose_name='Имя')),
                ('patronymic', models.CharField(default=None, max_length=64, verbose_name='Отчество')),
                ('email', models.EmailField(blank=True, default=None, max_length=254, verbose_name='Email')),
                ('isActive', models.BooleanField(default=True, verbose_name='Активно')),
            ],
            options={
                'verbose_name': 'Сотрудник',
                'verbose_name_plural': 'Сотрудники',
            },
        ),
    ]