# Generated by Django 2.1.7 on 2021-05-02 09:08

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_auto_20210320_1800'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='uuid_id',
            field=models.UUIDField(default=uuid.UUID('303e0854-2f69-4130-b1ae-d4dbddfd032b'), editable=False, primary_key=True, serialize=False),
        ),
    ]
