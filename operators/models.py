from django.conf import settings
from django.db import models

from companies.models import Company, Site


class Operator(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="operators"
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="operator_profile",
        null=True,
        blank=True
    )

    employee_id = models.CharField(
        max_length=50
    )

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100
    )

    phone = models.CharField(
        max_length=30,
        blank=True
    )

    site = models.ForeignKey(
        Site,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="operators"
    )

    is_active = models.BooleanField(
        default=True
    )

    date_joined = models.DateField(
        null=True,
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["first_name", "last_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "employee_id"],
                name="unique_operator_id_per_company"
            )
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"