from django.contrib import admin

from .models import HourMeterReading


@admin.register(HourMeterReading)
class HourMeterReadingAdmin(admin.ModelAdmin):

    list_display = (
        "equipment",
        "reading_date",
        "previous_reading",
        "current_reading",
        "hours_worked",
        "reading_type",
        "operator_name",
        "is_verified",
        "recorded_by",
    )

    list_filter = (
        "reading_type",
        "is_verified",
        "reading_date",
        "site",
    )

    search_fields = (
        "equipment__asset_number",
        "equipment__name",
        "operator_name",
        "remarks",
    )

    readonly_fields = (
        "hours_worked",
        "verified_at",
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "equipment",
        "site",
        "recorded_by",
        "verified_by",
    )

    ordering = (
        "-reading_date",
        "-created_at",
    )