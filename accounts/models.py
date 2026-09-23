from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Administrator"
        COMPANY_ADMIN = "company_admin", "Company Administrator"
        MANAGER = "manager", "Manager"
        SUPERVISOR = "supervisor", "Supervisor"
        OPERATOR = "operator", "Equipment Operator"
        MECHANIC = "mechanic", "Mechanic"
        VIEWER = "viewer", "Viewer"

    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.VIEWER,
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    employee_id = models.CharField(
        max_length=50,
        blank=True,
        unique=True,
        null=True,
    )

    is_active_operator = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.get_full_name() or self.username