# Generated by Django 5.0.4 on 2024-04-17 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, default='no description', verbose_name='توضیحات ')),
                ('log_level', models.CharField(default='INFO', max_length=255, verbose_name='سطح لوگ ')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='زمان و تاریخ ایجاد')),
            ],
            options={
                'verbose_name': 'لوگ',
                'verbose_name_plural': 'لوگ ها',
                'ordering': ['-created_at'],
            },
        ),
    ]
