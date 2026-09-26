from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from equipment.models import Equipment
from companies.models import Site


class HourMeterReading(models.Model):

    class ReadingType(models.TextChoices):
        DAILY = "daily", "Daily Reading"
        WEEKLY = "weekly", "Weekly Reading"
        MONTHLY = "monthly", "Monthly Reading"
        SERVICE = "service", "Service Reading"
        INITIAL = "initial", "Initial Reading"
        CORRECTION = "correction", "Correction"

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name="hour_meter_readings",
    )

    site = models.ForeignKey(
        Site,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hour_meter_readings",
    )

    reading_date = models.DateField()

    previous_reading = models.DecimalField(
        max_digits=12,
        decimal_places=1,
        default=Decimal("0.0"),
    )

    current_reading = models.DecimalField(
        max_digits=12,
        decimal_places=1,
    )

    hours_worked = models.DecimalField(
        max_digits=12,
        decimal_places=1,
        default=Decimal("0.0"),
        editable=False,
    )

    reading_type = models.CharField(
        max_length=20,
        choices=ReadingType.choices,
        default=ReadingType.DAILY,
    )

    operator_name = models.CharField(
        max_length=150,
        blank=True,
    )

    remarks = models.TextField(
        blank=True,
    )

    is_verified = models.BooleanField(
        default=False,
    )

    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_hour_meter_readings",
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_hour_meter_readings",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-reading_date",
            "-created_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "equipment",
                    "reading_date",
                ]
            ),
            models.Index(
                fields=[
                    "site",
                    "reading_date",
                ]
            ),
        ]

    def clean(self):
        super().clean()

        if self.previous_reading is None:
            self.previous_reading = Decimal("0.0")

        if self.current_reading is None:
            return

        if self.previous_reading < 0:
            raise ValidationError({
                "previous_reading":
                    "Previous hour-meter reading cannot be negative."
            })

        if self.current_reading < 0:
            raise ValidationError({
                "current_reading":
                    "Current hour-meter reading cannot be negative."
            })

        if self.current_reading < self.previous_reading:
            raise ValidationError({
                "current_reading":
                    "Current reading cannot be less than "
                    "the previous reading."
            })

        self.hours_worked = (
            self.current_reading -
            self.previous_reading
        )

    def save(self, *args, **kwargs):

        self.full_clean()

        self.hours_worked = (
            self.current_reading -
            self.previous_reading
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.equipment.asset_number} - "
            f"{self.current_reading} hrs - "
            f"{self.reading_date}"
        )