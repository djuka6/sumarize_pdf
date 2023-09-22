# Generated by Django 4.2.4 on 2023-09-01 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("PrepMind", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="savedresponse",
            old_name="data",
            new_name="answer",
        ),
        migrations.AddField(
            model_name="savedresponse",
            name="question",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
    ]
