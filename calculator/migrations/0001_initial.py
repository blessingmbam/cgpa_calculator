import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scale', models.FloatField(default=5.0)),
                ('grade_mapping', models.TextField(blank=True, default='')),
            ],
            options={
                'verbose_name_plural': 'Settings',
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_code', models.CharField(max_length=20)),
                ('units', models.IntegerField()),
                ('grade', models.CharField(max_length=5)),
                ('grade_point', models.FloatField()),
                ('semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='calculator.semester')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
