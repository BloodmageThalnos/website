# Generated by Django 2.1 on 2019-04-04 03:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0006_auto_20190331_1544'),
    ]

    operations = [
        migrations.CreateModel(
            name='DisqusModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('avatar', models.CharField(default='', max_length=64)),
                ('c_date', models.DateField(auto_now_add=True)),
                ('nickname', models.CharField(max_length=32)),
                ('username', models.CharField(max_length=32)),
                ('content', models.TextField()),
                ('picture', models.CharField(default='', max_length=64)),
                ('reply_to', models.IntegerField()),
            ],
        ),
    ]
