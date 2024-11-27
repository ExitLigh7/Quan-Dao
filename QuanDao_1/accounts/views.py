from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy
from QuanDao_1.accounts.forms import AppUserCreationForm, ProfileEditForm
from QuanDao_1.accounts.models import Profile

UserModel = get_user_model()


class UserLoginView(LoginView):
    template_name = 'accounts/login-page.html'

    # def get_success_url(self):
    #     return self.request.GET.get('next', '/')

class UserRegisterView(CreateView):
    model = UserModel
    template_name = 'accounts/register-page.html'
    form_class = AppUserCreationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)

        login(self.request, self.object)

        return response

class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = UserModel
    template_name = 'accounts/profile-details-page.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return self.request.user.profile

class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Profile
    template_name = 'accounts/profile-edit-page.html'
    form_class = ProfileEditForm

    def test_func(self):
        profile = get_object_or_404(Profile, pk=self.kwargs['pk'])
        return self.request.user == profile.user

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied("You are not allowed to edit this profile.")
        return obj

    def get_success_url(self):
        return reverse_lazy(
            'profile-details',
            kwargs={'pk': self.object.pk},
        )

from django.urls import reverse

class ProfileDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Profile

    def test_func(self):
        # Ensure the profile belongs to the currently logged-in user
        profile = self.get_object()
        return self.request.user == profile.user

    def get(self, request, *args, **kwargs):
        # Override GET to prevent rendering a confirmation page
        return HttpResponse(status=405)  # Method Not Allowed

    def delete(self, request, *args, **kwargs):
        print(f"Delete method triggered for profile {kwargs.get('pk')}")

        if request.method == 'POST':
            # Log out the user
            logout(request)

            try:
                # Fetch the profile and associated user
                profile = self.get_object()
                user = profile.user

                # Delete the user (Profile is deleted due to CASCADE)
                print(f"Deleting user: {user.username}")
                user.delete()

                # Success message
                messages.success(request, "Your profile and account have been deleted successfully.")
            except Exception as e:
                print(f"Error: {e}")
                messages.error(request, "An error occurred while deleting your profile.")

        return redirect(self.get_success_url())

    def get_success_url(self):
        # Example: Redirecting to a user-specific page, or a static URL
        return reverse('home')



