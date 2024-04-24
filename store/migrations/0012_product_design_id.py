# Generated by Django 5.0.2 on 2024-04-24 13:19

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_product_design'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='design_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
