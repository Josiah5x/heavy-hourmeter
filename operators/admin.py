from django.contrib import admin

from .models import Operator


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):

    list_display = (
        "employee_id",
        "first_name",
        "last_name",
        "company",
        "site",
        "phone",
        "is_active",
    )

    list_filter = (
        "company",
        "site",
        "is_active",
    )

    search_fields = (
        "employee_id",
        "first_name",
        "last_name",
        "phone",
    )