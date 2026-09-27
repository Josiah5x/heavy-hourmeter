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





class ServiceRecord(models.Model):

    class ServiceType(models.TextChoices):
        A = "A", "A Service"
        A2 = "A2", "A2 Service"
        B = "B", "B Service"
        C = "C", "C Service"
        D = "D", "D Service"
        OTHER = "OTHER", "Other"

    class ServiceStatus(models.TextChoices):
        NOT_DUE = "not_due", "Not Due"
        DUE_SOON = "due_soon", "Due Soon"
        DUE = "due", "Due"
        OVERDUE = "overdue", "Overdue"

    class AirFilterStatus(models.TextChoices):
        NOT_DUE = "not_due", "Not Due"
        SERVICE = "service", "Service"

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name="service_records"
    )

    service_date = models.DateField()

    service_type = models.CharField(
        max_length=20,
        choices=ServiceType.choices
    )

    hour_meter_at_service = models.DecimalField(
        max_digits=12,
        decimal_places=1,
        default=0
    )

    service_interval = models.DecimalField(
        max_digits=12,
        decimal_places=1,
        default=250
    )

    next_service = models.DecimalField(
        max_digits=12,
        decimal_places=1,
        editable=False
    )

    air_filter_status = models.CharField(
        max_length=20,
        choices=AirFilterStatus.choices,
        default=AirFilterStatus.NOT_DUE
    )

    notes = models.TextField(
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_service_records"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-service_date", "-id"]

    def save(self, *args, **kwargs):

        self.next_service = (
            self.hour_meter_at_service
            + self.service_interval
        )

        super().save(*args, **kwargs)


    @property
    def current_hm(self):
        return self.equipment.current_hours

    @property
    def remaining_hours(self):

        current = self.equipment.current_hours or 0
        next_service = self.next_service or 0

        return next_service - current



    @property
    def service_status(self):

        remaining = self.remaining_hours

        if remaining <= 0:
            return "overdue"

        if remaining <= 50:
            return "due"

        if remaining <= 100:
            return "due_soon"

        return "not_due"

   