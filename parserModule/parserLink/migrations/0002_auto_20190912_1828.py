# Generated by Django 2.2.1 on 2019-09-12 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parserLink', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dblog',
            name='httpMethod',
            field=models.CharField(max_length=10),
        ),
    ]
