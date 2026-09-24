from django.contrib import admin

from .models import Company, Site


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "short_name",
        "phone",
        "email",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "short_name",
        "phone",
        "email",
        "address",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
    )

    ordering = (
        "name",
    )

    fieldsets = (
        (
            "Company Information",
            {
                "fields": (
                    "name",
                    "short_name",
                    "logo",
                    "is_active",
                )
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    "address",
                    "phone",
                    "email",
                    "website",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_by",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "company",
        "city",
        "state",
        "country",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "country",
        "state",
        "company",
        "created_at",
    )

    search_fields = (
        "name",
        "code",
        "company__name",
        "address",
        "city",
        "state",
        "contact_person",
        "contact_phone",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
    )

    ordering = (
        "company",
        "name",
    )

    autocomplete_fields = (
        "company",
    )

    fieldsets = (
        (
            "Site Information",
            {
                "fields": (
                    "company",
                    "name",
                    "code",
                    "is_active",
                )
            },
        ),
        (
            "Location",
            {
                "fields": (
                    "address",
                    "city",
                    "state",
                    "country",
                    "latitude",
                    "longitude",
                )
            },
        ),
        (
            "Contact",
            {
                "fields": (
                    "contact_person",
                    "contact_phone",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_by",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )