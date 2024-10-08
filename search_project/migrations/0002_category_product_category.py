# Generated by Django 4.2.16 on 2024-09-23 03:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("search_project", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
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
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name="product",
            name="category",
            field=models.CharField(default="default_category", max_length=100),
        ),
    ]
