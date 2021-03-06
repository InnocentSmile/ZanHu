# Generated by Django 2.1.7 on 2021-03-20 10:00

from django.conf import settings
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='liked',
            field=models.ManyToManyField(related_name='liked_news', to=settings.AUTH_USER_MODEL, verbose_name='点赞用户'),
        ),
        migrations.AlterField(
            model_name='news',
            name='uuid_id',
            field=models.UUIDField(default=uuid.UUID('668df256-087a-48b6-9ab6-210e4a5560c9'), editable=False, primary_key=True, serialize=False),
        ),
    ]
