# Generated by Django 5.0.7 on 2025-02-12 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='uid',
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
    ]
