# Generated by Django 2.2.4 on 2019-09-21 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nicetable', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='columnpersistence',
            name='visible',
            field=models.BooleanField(default=True),
        ),
    ]
