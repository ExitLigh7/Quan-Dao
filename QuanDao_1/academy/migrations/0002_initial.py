# Generated by Django 5.1.3 on 2024-11-22 19:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('academy', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='feedback',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='martialartsclass',
            name='instructor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='classes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='feedback',
            name='class_instance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='academy.martialartsclass'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='martial_arts_class',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='academy.martialartsclass'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='instructor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='schedule',
            name='martial_arts_class',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='academy.martialartsclass'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='schedule',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='enrollments', to='academy.schedule'),
        ),
        migrations.AlterUniqueTogether(
            name='feedback',
            unique_together={('user', 'class_instance')},
        ),
        migrations.AlterUniqueTogether(
            name='schedule',
            unique_together={('martial_arts_class', 'date', 'start_time')},
        ),
        migrations.AlterUniqueTogether(
            name='enrollment',
            unique_together={('user', 'martial_arts_class')},
        ),
    ]
