# Generated by Django 2.1 on 2019-04-08 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VisitModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=20)),
                ('v_time', models.DateTimeField(auto_now_add=True)),
                ('user_id', models.IntegerField()),
                ('user_ip_hash', models.IntegerField()),
                ('duration', models.IntegerField()),
            ],
        ),
    ]
