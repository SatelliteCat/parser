# Generated by Django 2.2.1 on 2019-09-15 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parserLink', '0003_ip_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dblog',
            name='httpMethod',
            field=models.CharField(db_index=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='dblog',
            name='ipAddress',
            field=models.CharField(db_index=True, max_length=15),
        ),
    ]
