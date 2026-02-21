from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, Bank

@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    fieldsets = [
        (None, {
            'fields': (
                'username', 'email', 'password', 'registered_date'
            ),
        }),
    ]
    readonly_fields = ['registered_date']

admin.site.register(Bank)