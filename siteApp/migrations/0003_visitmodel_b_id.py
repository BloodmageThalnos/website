# Generated by Django 2.1 on 2019-04-13 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('siteApp', '0002_auto_20190408_1725'),
    ]

    operations = [
        migrations.AddField(
            model_name='visitmodel',
            name='b_id',
            field=models.CharField(default='', max_length=64),
            preserve_default=False,
        ),
    ]
