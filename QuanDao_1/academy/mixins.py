from django.contrib.auth.mixins import UserPassesTestMixin


class IsInstructorMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_staff or self.request.user.profile.role == 'instructor'
        )
