from django.db.models.signals import post_save
from django.dispatch import receiver
from QuanDao_1.academy.models import Enrollment

from QuanDao_1.academy.tasks import send_enrollment_email


@receiver(post_save, sender=Enrollment)
def send_enrollment_notification(sender, instance, created, **kwargs):
    if created:
        subject = f"Successful Enrollment for {instance.martial_arts_class.name} - {instance.schedule.date}"
        message = (
            f"Hello, {instance.user.username}!, \n\n"
            f"you have successfully enrolled for class: {instance.martial_arts_class.name},\n"
            f"scheduled for {instance.schedule.date} starting at {instance.schedule.start_time}."
        )
        from_email = "test@test.com"
        recipient_list = [instance.user.email]

        send_enrollment_email.delay(subject, message, from_email, recipient_list)
