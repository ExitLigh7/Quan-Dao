from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

UserModel = get_user_model()

class MartialArtsClass(models.Model):
    name = models.CharField(
        max_length=100
    )

    description = models.TextField()

    level_choices = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    level = models.CharField(
        max_length=30,
        choices=level_choices,
        default='beginner'
    )

    max_capacity = models.PositiveIntegerField()

    instructor = models.ForeignKey(
        UserModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classes',
    )

    slug = models.SlugField(
        unique=True,
        max_length=100,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Schedule(models.Model):
    martial_arts_class = models.ForeignKey(
        MartialArtsClass,
        on_delete=models.CASCADE,
        related_name='schedules'
    )

    instructor = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='schedules'
    )

    date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    class Meta:
        unique_together = ('martial_arts_class', 'date', 'start_time')

    def __str__(self):
        return f"{self.martial_arts_class.name} - {self.date} {self.start_time}"

class Enrollment(models.Model):
    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='enrollments',
    )

    martial_arts_class = models.ForeignKey(
        MartialArtsClass,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enrollments')

    enrollment_date = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        unique_together = ('user', 'martial_arts_class')

    def __str__(self):
        return f"{self.user.username} - {self.martial_arts_class.name}"

class Feedback(models.Model):
    class_instance = models.ForeignKey(
        MartialArtsClass,
        on_delete=models.CASCADE,
        related_name='feedbacks',
    )

    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='feedbacks',
    )

    rating = models.PositiveIntegerField(
        choices=[
            (i, str(i)) for i in range(1, 6)],
    )

    comment = models.TextField(
        blank=True,
        null=True,
    )

    created_on = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"Feedback from {self.user.username} for {self.class_instance.name}"

    class Meta:
        unique_together = ['user', 'class_instance']
        ordering = ['-created_on']
