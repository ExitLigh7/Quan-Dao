from django.contrib import admin
from .models import Profile, AppUser


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


@admin.register(AppUser)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'get_full_name', 'get_role', 'is_staff', 'is_active', 'get_joined_on')
    list_filter = ('is_staff', 'is_active', 'profile__role')
    search_fields = ('username', 'email', 'profile__first_name', 'profile__last_name', 'profile__role')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    inlines = [ProfileInline]
    readonly_fields = ('last_login', 'is_active')

    # Display full name as a computed field
    def get_full_name(self, obj):
        return obj.profile.get_full_name() if obj.profile else 'No profile'

    get_full_name.short_description = 'Full Name'

    def get_role(self, obj):
        return obj.profile.role if obj.profile else 'No role'
    get_role.short_description = 'Role'

    def get_joined_on(self, obj):
        return obj.profile.joined_on if obj.profile else 'No join date'

    get_joined_on.short_description = 'Joined On'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'role', 'date_of_birth', 'profile_picture', 'joined_on')
    list_filter = ('role', 'date_of_birth')
    search_fields = ('first_name', 'last_name', 'role', 'user__username', 'user__email')
    ordering = ('joined_on',)
    readonly_fields = ('user',)
