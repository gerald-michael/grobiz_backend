# Generated by Django 3.2.8 on 2021-10-10 16:34

import accounts.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_smeprofile_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvestorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_image', models.ImageField(upload_to=accounts.models.upload_profile_image)),
                ('name', models.CharField(blank=True, max_length=255, verbose_name='Name of Investor')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='investor_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
