# Generated by Django 4.2.7 on 2023-12-19 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shortlinks', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='link',
            index=models.Index(fields=['short_path'], name='shortlinks__short_p_179f6f_idx'),
        ),
    ]
