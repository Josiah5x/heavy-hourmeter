from django.conf import settings
from django.db import models


class Company(models.Model):

    name = models.CharField(
        max_length=200,
        unique=True
    )

    short_name = models.CharField(
        max_length=50,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    phone = models.CharField(
        max_length=50,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    website = models.URLField(
        blank=True
    )

    logo = models.ImageField(
        upload_to="companies/logos/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_companies"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class Site(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="sites"
    )

    name = models.CharField(
        max_length=200
    )

    code = models.CharField(
        max_length=50,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    city = models.CharField(
        max_length=100,
        blank=True
    )

    state = models.CharField(
        max_length=100,
        blank=True
    )

    country = models.CharField(
        max_length=100,
        default="Nigeria"
    )

    contact_person = models.CharField(
        max_length=150,
        blank=True
    )

    contact_phone = models.CharField(
        max_length=50,
        blank=True
    )

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_sites"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["company", "name"]
        verbose_name = "Site"
        verbose_name_plural = "Sites"

        constraints = [
            models.UniqueConstraint(
                fields=["company", "name"],
                name="unique_site_name_per_company"
            ),

            models.UniqueConstraint(
                fields=["company", "code"],
                name="unique_site_code_per_company"
            ),
        ]

    def __str__(self):
        return f"{self.company.name} - {self.name}"