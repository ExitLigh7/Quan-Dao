from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy
from QuanDao_1.accounts.forms import AppUserCreationForm, ProfileEditForm
from QuanDao_1.accounts.models import Profile

UserModel = get_user_model()


class UserLoginView(LoginView):
    template_name = 'accounts/login-page.html'

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


class ProfileDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Profile
    template_name = 'accounts/profile-delete-page.html'
    success_url = reverse_lazy('login')

    def test_func(self):
        profile = get_object_or_404(Profile, pk=self.kwargs['pk'])
        return self.request.user == profile.user

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Log out the user using the request object
        logout(request)
        # Delete the associated AppUser (which cascades to the profile)
        self.object.user.delete()
        return redirect(self.success_url)



