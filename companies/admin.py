from django.contrib import admin

from .models import Company, Site


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "phone",
        "email",
        "is_active",
    )

    search_fields = (
        "name",
        "code",
    )


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "company",
        "is_active",
    )

    list_filter = (
        "company",
        "is_active",
    )

    search_fields = (
        "name",
        "code",
    )