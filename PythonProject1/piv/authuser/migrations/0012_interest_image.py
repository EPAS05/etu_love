# Generated by Django 4.2.20 on 2025-04-01 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authuser', '0011_remove_profile_photo1_remove_profile_photo2_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='interest',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='interests/'),
        ),
    ]
