from django.conf import settings
from django.db import models

from companies.models import Company, Site


class Equipment(models.Model):

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        IDLE = "idle", "Idle"
        MAINTENANCE = "maintenance", "Under Maintenance"
        OUT_OF_SERVICE = "out_of_service", "Out of Service"
        RETIRED = "retired", "Retired"

    class EquipmentType(models.TextChoices):
        EXCAVATOR = "excavator", "Excavator"
        BULLDOZER = "bulldozer", "Bulldozer"
        LOADER = "loader", "Wheel Loader"
        GRADER = "grader", "Motor Grader"
        CRANE = "crane", "Crane"
        DUMPER = "dumper", "Dump Truck"
        TRACTOR = "tractor", "Tractor"
        GENERATOR = "generator", "Generator"
        COMPRESSOR = "compressor", "Compressor"
        FORKLIFT = "forklift", "Forklift"
        OTHER = "other", "Other"

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="equipment"
    )

    site = models.ForeignKey(
        Site,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipment"
    )

    asset_number = models.CharField(
        max_length=50
    )

    name = models.CharField(
        max_length=200
    )

    equipment_type = models.CharField(
        max_length=30,
        choices=EquipmentType.choices
    )

    manufacturer = models.CharField(
        max_length=100,
        blank=True
    )

    model = models.CharField(
        max_length=100,
        blank=True
    )

    serial_number = models.CharField(
        max_length=150,
        blank=True
    )

    registration_number = models.CharField(
        max_length=100,
        blank=True
    )

    year = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    current_hours = models.DecimalField(
        max_digits=12,
        decimal_places=1,
        default=0
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    image = models.ImageField(
        upload_to="equipment/",
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True
    )

    purchase_date = models.DateField(
        null=True,
        blank=True
    )

    commissioning_date = models.DateField(
        null=True,
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_equipment"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["asset_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "asset_number"],
                name="unique_asset_number_per_company"
            )
        ]

    def __str__(self):
        return f"{self.asset_number} - {self.name}"