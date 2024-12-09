from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from QuanDao_1.accounts.models import Profile

User = get_user_model()

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, role='admin' if instance.is_superuser else 'student')
    else:
        if instance.is_superuser:
            instance.profile.role = 'admin'
            instance.profile.save()

