# Generated by Django 2.1 on 2019-03-31 06:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0003_auto_20190318_1715'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlemodel',
            name='type',
            field=models.IntegerField(default=1),
        ),
    ]
