# Generated by Django 5.1.3 on 2024-11-27 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academy', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='martialartsclass',
            name='slug',
            field=models.SlugField(blank=True, max_length=100, unique=True),
        ),
    ]