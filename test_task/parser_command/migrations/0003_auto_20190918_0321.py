# Generated by Django 2.2.1 on 2019-09-17 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parser_command', '0002_auto_20190918_0126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False, unique=True),
        ),
    ]