# Generated by Django 5.1.7 on 2025-05-15 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0017_profile_enable_2fa'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='order',
            field=models.IntegerField(default=0),
        ),
    ]
