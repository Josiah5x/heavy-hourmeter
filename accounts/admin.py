from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        (
            "Company System",
            {
                "fields": (
                    "role",
                    "phone",
                    "employee_id",
                    "is_active_operator",
                )
            }
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Company System",
            {
                "fields": (
                    "role",
                    "phone",
                    "employee_id",
                    "is_active_operator",
                )
            }
        ),
    )