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

    


from decimal import Decimal

from django.contrib import admin
from django.utils.html import format_html

from .models import ServiceRecord


@admin.register(ServiceRecord)
class ServiceRecordAdmin(admin.ModelAdmin):

    # =================================================
    # LIST DISPLAY
    # =================================================

    list_display = (
        "service_date",
        "equipment_info",
        "site_name",
        "service_type_badge",
        "hour_meter_at_service_display",
        "next_service_display",
        "current_hm_display",
        "remaining_display",
        "service_status_badge",
        "air_filter_badge",
        "created_by",
    )

    # =================================================
    # FILTERS
    # =================================================

    list_filter = (
        "service_type",
        "air_filter_status",
        "service_date",
        "equipment__company",
        "equipment__site",
    )

    # =================================================
    # SEARCH
    # =================================================

    search_fields = (
        "equipment__asset_number",
        "equipment__name",
        "equipment__manufacturer",
        "equipment__model",
        "equipment__serial_number",
        "notes",
    )

    # =================================================
    # DATE NAVIGATION
    # =================================================

    date_hierarchy = "service_date"

    # =================================================
    # ORDERING
    # =================================================

    ordering = (
        "-service_date",
        "-id",
    )

    # =================================================
    # PERFORMANCE
    # =================================================

    list_select_related = (
        "equipment",
        "equipment__company",
        "equipment__site",
        "created_by",
    )

    # =================================================
    # PAGINATION
    # =================================================

    list_per_page = 25

    # =================================================
    # READ ONLY FIELDS
    # =================================================

    readonly_fields = (
        "next_service",
        "current_hm_admin",
        "remaining_hours_admin",
        "service_status_admin",
        "created_at",
        "updated_at",
    )

    # =================================================
    # FIELDSETS
    # =================================================

    fieldsets = (

        (
            "Equipment",
            {
                "fields": (
                    "equipment",
                    "service_date",
                    "service_type",
                )
            },
        ),

        (
            "Hour Meter & Service Schedule",
            {
                "fields": (
                    "hour_meter_at_service",
                    "service_interval",
                    "next_service",
                    "current_hm_admin",
                    "remaining_hours_admin",
                    "service_status_admin",
                )
            },
        ),

        (
            "Maintenance",
            {
                "fields": (
                    "air_filter_status",
                    "notes",
                )
            },
        ),

        (
            "Audit Information",
            {
                "fields": (
                    "created_by",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    # =================================================
    # MACHINE
    # =================================================

    @admin.display(
        description="Machine",
        ordering="equipment__name",
    )
    def equipment_info(self, obj):

        return format_html(
            "<strong>{}</strong><br>"
            "<small style='color:#777'>{}</small>",
            obj.equipment.name,
            obj.equipment.asset_number,
        )

    # =================================================
    # LOCATION
    # =================================================

    @admin.display(
        description="Location",
        ordering="equipment__site__name",
    )
    def site_name(self, obj):

        if obj.equipment.site:
            return obj.equipment.site.name

        return "—"

    # =================================================
    # SERVICE TYPE
    # =================================================

    @admin.display(
        description="Service Type",
    )
    def service_type_badge(self, obj):

        colors = {
            "A": "#198754",
            "A2": "#0d6efd",
            "B": "#6f42c1",
            "C": "#fd7e14",
            "D": "#dc3545",
            "OTHER": "#6c757d",
        }

        color = colors.get(
            obj.service_type,
            "#6c757d",
        )

        return format_html(
            '<span style="'
            'background:{};'
            'color:white;'
            'padding:4px 8px;'
            'border-radius:5px;'
            'font-weight:600;">'
            '{}</span>',
            color,
            obj.get_service_type_display(),
        )

    # =================================================
    # HM AT SERVICE
    # =================================================

    @admin.display(
        description="HM Service",
        ordering="hour_meter_at_service",
    )
    def hour_meter_at_service_display(self, obj):

        value = Decimal(str(obj.hour_meter_at_service or "0"))

        return f"{value:,.1f}"

    # =================================================
    # NEXT SERVICE
    # =================================================

    @admin.display(
        description="Next Service",
        ordering="next_service",
    )
    def next_service_display(self, obj):

        value = Decimal(str(obj.next_service or "0"))

        return f"{value:,.1f}"

    # =================================================
    # CURRENT HM
    # =================================================

    @admin.display(
        description="Current HM",
    )
    def current_hm_display(self, obj):

        value = Decimal(
            str(obj.current_hm or "0")
        )

        return f"{value:,.1f}"

    # =================================================
    # REMAINING HOURS
    # =================================================

    @admin.display(
        description="Remaining",
    )
    def remaining_display(self, obj):

        value = Decimal(
            str(obj.remaining_hours or "0")
        )

        formatted = f"{value:,.1f}"

        if value <= Decimal("0"):

            return format_html(
                '<strong style="color:#dc3545;">'
                '{}'
                '</strong>',
                formatted,
            )

        if value <= Decimal("50"):

            return format_html(
                '<strong style="color:#dc3545;">'
                '{}'
                '</strong>',
                formatted,
            )

        if value <= Decimal("100"):

            return format_html(
                '<strong style="color:#fd7e14;">'
                '{}'
                '</strong>',
                formatted,
            )

        return format_html(
            '<strong style="color:#198754;">'
            '{}'
            '</strong>',
            formatted,
        )

    # =================================================
    # SERVICE STATUS
    # =================================================

    @admin.display(
        description="Status",
    )
    def service_status_badge(self, obj):

        status = obj.service_status

        labels = {
            "not_due": "NOT DUE",
            "due_soon": "DUE SOON",
            "due": "DUE",
            "overdue": "OVERDUE",
        }

        colors = {
            "not_due": "#198754",
            "due_soon": "#0d6efd",
            "due": "#fd7e14",
            "overdue": "#dc3545",
        }

        color = colors.get(
            status,
            "#6c757d",
        )

        label = labels.get(
            status,
            status,
        )

        return format_html(
            '<span style="'
            'background:{};'
            'color:white;'
            'padding:4px 8px;'
            'border-radius:5px;'
            'font-weight:600;">'
            '{}'
            '</span>',
            color,
            label,
        )

    # =================================================
    # AIR FILTER
    # =================================================

    @admin.display(
        description="Air Filter",
    )
    def air_filter_badge(self, obj):

        if obj.air_filter_status == "service":

            return format_html(
                '<span style="'
                'background:#dc3545;'
                'color:white;'
                'padding:4px 8px;'
                'border-radius:5px;'
                'font-weight:600;">'
                'SERVICE'
                '</span>'
            )

        return format_html(
            '<span style="'
            'background:#198754;'
            'color:white;'
            'padding:4px 8px;'
            'border-radius:5px;'
            'font-weight:600;">'
            'NOT DUE'
            '</span>'
        )

    # =================================================
    # CALCULATED VALUES IN DETAIL PAGE
    # =================================================

    @admin.display(
        description="Current Hour Meter",
    )
    def current_hm_admin(self, obj):

        value = Decimal(
            str(obj.current_hm or "0")
        )

        return f"{value:,.1f}"

    @admin.display(
        description="Remaining Hours",
    )
    def remaining_hours_admin(self, obj):

        value = Decimal(
            str(obj.remaining_hours or "0")
        )

        return f"{value:,.1f}"

    @admin.display(
        description="Service Status",
    )
    def service_status_admin(self, obj):

        labels = {
            "not_due": "Not Due",
            "due_soon": "Due Soon",
            "due": "Due",
            "overdue": "Overdue",
        }

        return labels.get(
            obj.service_status,
            obj.service_status,
        )
