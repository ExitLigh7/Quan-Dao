from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Profile(models.Model):
    STUDENT = 'student'
    INSTRUCTOR = 'instructor'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (INSTRUCTOR, 'Instructor'),
        (ADMIN, 'Admin'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )

    first_name = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    last_name = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=STUDENT
    )

    biography = models.TextField(
        blank=True,
        null=True
    )

    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )

    joined_on = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):
        if self.user.is_superuser:
            self.role = self.ADMIN
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def is_complete(self):
        return bool(self.first_name and self.last_name and self.date_of_birth)

    def delete(self, *args, **kwargs):
        self.user.delete()
        super().delete(*args, **kwargs)
