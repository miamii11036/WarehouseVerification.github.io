# Generated by Django 5.1.3 on 2024-12-03 14:45

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myweb", "0002_alter_userinfo_password"),
    ]

    operations = [
        migrations.CreateModel(
            name="OrderList",
            fields=[
                ("order_id", models.AutoField(primary_key=True, serialize=False)),
                ("year", models.IntegerField()),
                (
                    "month",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(12),
                        ]
                    ),
                ),
                ("region", models.CharField(max_length=100)),
                ("client", models.CharField(max_length=100)),
                ("status", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="OrderDetail",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("product_id", models.IntegerField()),
                ("product_name", models.CharField(max_length=100)),
                ("quantity", models.IntegerField()),
                ("package", models.CharField()),
                (
                    "order_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="myweb.orderlist",
                    ),
                ),
            ],
        ),
    ]
