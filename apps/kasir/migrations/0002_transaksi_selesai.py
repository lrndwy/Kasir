# Generated by Django 5.1.3 on 2024-11-19 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kasir', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaksi',
            name='selesai',
            field=models.BooleanField(default=False),
        ),
    ]
