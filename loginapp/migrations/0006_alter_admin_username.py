# Generated by Django 2.1 on 2021-01-11 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loginapp', '0005_alter_admins'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=64, unique=True),
        ),
    ]
