from django import forms
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from datetime import timedelta
from .models import Schedule
from django.db.models import Q

class ScheduleBaseForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['martial_arts_class', 'instructor', 'date', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < now().date():
            raise ValidationError("The date cannot be in the past.")
        return date

    def clean_start_time(self):
        date = self.cleaned_data.get('date')
        start_time = self.cleaned_data.get('start_time')
        current_time = now()

        if date == current_time.date() and start_time is not None:
            # Ensure the start time is at least 4 hours from now if the date is today
            if start_time < (current_time + timedelta(hours=4)).time():
                raise ValidationError("The start time must be at least 4 hours from now.")
        return start_time

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        martial_arts_class = cleaned_data.get('martial_arts_class')
        instructor = cleaned_data.get('instructor')

        # Validate that end time is after start time
        if start_time and end_time and start_time >= end_time:
            raise ValidationError("The end time must be after the start time.")

        # Overlapping schedule validation
        if date and start_time and end_time:
            overlapping_schedules = Schedule.objects.filter(
                date=date,
                start_time__lt=end_time,
                end_time__gt=start_time,
            ).filter(
                Q(martial_arts_class=martial_arts_class) | Q(instructor=instructor)
            )

            # Exclude the current instance if updating
            if self.instance.pk:
                overlapping_schedules = overlapping_schedules.exclude(pk=self.instance.pk)

            if overlapping_schedules.exists():
                raise ValidationError("This schedule conflicts with an existing one.")

        return cleaned_data



class ScheduleCreateForm(ScheduleBaseForm):
    class Meta(ScheduleBaseForm.Meta):
        exclude = ['instructor']

class ScheduleEditForm(ScheduleBaseForm):
    class Meta(ScheduleBaseForm.Meta):
        exclude = ['instructor']

