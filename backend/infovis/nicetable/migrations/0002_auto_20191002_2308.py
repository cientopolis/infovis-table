# Generated by Django 2.2.4 on 2019-10-02 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nicetable', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='columnpersistence',
            name='index',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='columnpersistence',
            name='title',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
