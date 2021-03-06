# Generated by Django 2.1.7 on 2019-02-27 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CaptchaRecord',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('hash', models.CharField(max_length=40)),
                ('user', models.CharField(max_length=30)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('pic', models.CharField(max_length=30)),
                ('answer', models.CharField(max_length=30)),
                ('wrong_times', models.IntegerField(default=0)),
                ('correct', models.IntegerField(default=0)),
            ],
        ),
    ]
