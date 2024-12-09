from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from QuanDao_1.accounts.models import Profile

UserModel = get_user_model()


class AppUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = UserModel
        fields = ('username', 'email')

class AppUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = UserModel

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user', 'role')
        widgets = {
            'biograpy': forms.Textarea(attrs={'rows': 4}),  # Optional: Customizes the widget
        }
        help_texts = {
            'biography': 'The field is optional.',
            'profile_picture': 'The field is optional.',
        }
