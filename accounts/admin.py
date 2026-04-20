from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import Account, UserProfile
from .forms import AccountCreationForm, AccountChangeForm
from django.utils.html import format_html

# Register your models here.

class AccountAdmin(UserAdmin):
    form = AccountChangeForm
    add_form = AccountCreationForm

    list_display = ('email', 'first_name', 'last_name', 'username', 'phone_number', 'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)

    fieldsets = (
        ('Account Information', {'fields': ('email', 'username', 'password')}),
        ('Personal Information', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_admin', 'is_superadmin')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'username', 'first_name', 'last_name', 'phone_number', 'password1', 'password2'),
            },
        ),
    )

    filter_horizontal = ()
    list_filter = ('is_active', 'is_staff', 'is_admin', 'is_superadmin')

class UserProfileAdmin(admin.ModelAdmin):
    @admin.display(description='Profile Picture')
    def thumbnail(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="30" style="border-radius:50%;">', obj.profile_picture.url)
        return 'No image'

    list_display = ('thumbnail', 'user', 'city', 'state', 'country')

admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

# Hide default Django Group model from admin UI.
# This does not affect authentication; it only removes Group management from admin.
admin.site.unregister(Group)
