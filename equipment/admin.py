from django.contrib import admin

from .models import Equipment


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):

    list_display = (
        "asset_number",
        "name",
        "equipment_type",
        "manufacturer",
        "model",
        "site",
        "current_hours",
        "status",
    )

    list_filter = (
        "equipment_type",
        "status",
        "company",
        "site",
    )

    search_fields = (
        "asset_number",
        "name",
        "serial_number",
        "registration_number",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )