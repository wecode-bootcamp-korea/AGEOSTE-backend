# Generated by Django 3.1.5 on 2021-01-20 00:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
        ('user', '0001_initial'),
        ('order', '0002_auto_20210119_2327'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CartItem',
            new_name='Cart',
        ),
        migrations.AlterModelTable(
            name='cart',
            table='carts',
        ),
    ]
