# Generated by Django 4.1.4 on 2023-02-02 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_alter_dataapi_processed_at_alter_dataapi_receipt'),
    ]

    operations = [
        migrations.AddField(
            model_name='inference',
            name='customer_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]