# Generated by Django 5.0.2 on 2024-04-18 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_alter_product_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='design',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
