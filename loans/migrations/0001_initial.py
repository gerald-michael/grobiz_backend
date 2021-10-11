# Generated by Django 3.2.8 on 2021-10-08 10:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Loans',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=22, null=True)),
                ('status', models.CharField(choices=[('PAID', 'paid'), ('PENDING', 'pending'), ('APPROVED', 'approved')], default='PENDING', max_length=50, verbose_name='Status')),
                ('interest', models.FloatField()),
                ('date_paid', models.DateTimeField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
