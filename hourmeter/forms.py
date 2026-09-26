from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError

from .models import HourMeterReading
from equipment.models import Equipment
from companies.models import Site


class HourMeterReadingForm(forms.ModelForm):

    class Meta:
        model = HourMeterReading

        fields = [
            "equipment",
            "site",
            "reading_date",
            "previous_reading",
            "current_reading",
            "reading_type",
            "operator_name",
            "remarks",
            "is_verified",
        ]

        widgets = {

            "equipment": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "site": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "reading_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "previous_reading": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                    "min": "0",
                    "placeholder": "0.0",
                }
            ),

            "current_reading": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                    "min": "0",
                    "placeholder": "0.0",
                }
            ),

            "reading_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "operator_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Operator name",
                }
            ),

            "remarks": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Enter remarks about this hour-meter reading..."
                    ),
                }
            ),

            "is_verified": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

        labels = {
            "equipment": "Equipment",
            "site": "Operating Site",
            "reading_date": "Reading Date",
            "previous_reading": "Previous Reading",
            "current_reading": "Current Reading",
            "reading_type": "Reading Type",
            "operator_name": "Operator",
            "remarks": "Remarks",
            "is_verified": "Mark as Verified",
        }

        help_texts = {
            "previous_reading": (
                "The previous recorded hour-meter value."
            ),

            "current_reading": (
                "The current value displayed on the machine."
            ),

            "is_verified": (
                "Only authorized users should verify readings."
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # ------------------------------------------------------
        # Equipment
        # ------------------------------------------------------

        self.fields["equipment"].queryset = (
            Equipment.objects
            .select_related("company", "site")
            .order_by("asset_number")
        )

        # ------------------------------------------------------
        # Sites
        # ------------------------------------------------------

        self.fields["site"].queryset = (
            Site.objects
            .filter(is_active=True)
            .select_related("company")
            .order_by("company__name", "name")
        )

        # Site is optional
        self.fields["site"].required = False

        # Operator is optional
        self.fields["operator_name"].required = False

        # Remarks optional
        self.fields["remarks"].required = False

        # ------------------------------------------------------
        # Automatically determine previous reading
        # ------------------------------------------------------

        if self.instance and self.instance.pk:

            # Editing an existing reading.
            #
            # Keep its original previous reading.
            if self.instance.previous_reading is not None:

                self.fields[
                    "previous_reading"
                ].initial = self.instance.previous_reading

        elif self.initial.get("equipment"):

            try:

                equipment_id = self.initial.get("equipment")

                equipment = Equipment.objects.get(
                    pk=equipment_id
                )

                self.fields[
                    "previous_reading"
                ].initial = equipment.current_hours

            except Equipment.DoesNotExist:

                pass

    # ==========================================================
    # EQUIPMENT
    # ==========================================================

    def clean_equipment(self):

        equipment = self.cleaned_data.get(
            "equipment"
        )

        if not equipment:
            raise ValidationError(
                "Please select equipment."
            )

        return equipment

    # ==========================================================
    # PREVIOUS READING
    # ==========================================================

    def clean_previous_reading(self):

        value = self.cleaned_data.get(
            "previous_reading"
        )

        if value is None:
            value = Decimal("0.0")

        if value < 0:

            raise ValidationError(
                "Previous hour-meter reading cannot be negative."
            )

        return value

    # ==========================================================
    # CURRENT READING
    # ==========================================================

    def clean_current_reading(self):

        value = self.cleaned_data.get(
            "current_reading"
        )

        if value is None:

            raise ValidationError(
                "Current hour-meter reading is required."
            )

        if value < 0:

            raise ValidationError(
                "Current hour-meter reading cannot be negative."
            )

        return value

    # ==========================================================
    # DATE
    # ==========================================================

    def clean_reading_date(self):

        reading_date = self.cleaned_data.get(
            "reading_date"
        )

        if not reading_date:

            raise ValidationError(
                "Reading date is required."
            )

        return reading_date

    # ==========================================================
    # MAIN VALIDATION
    # ==========================================================

    def clean(self):

        cleaned_data = super().clean()

        equipment = cleaned_data.get(
            "equipment"
        )

        previous = cleaned_data.get(
            "previous_reading"
        )

        current = cleaned_data.get(
            "current_reading"
        )

        reading_date = cleaned_data.get(
            "reading_date"
        )

        site = cleaned_data.get(
            "site"
        )

        # ------------------------------------------------------
        # Compare readings
        # ------------------------------------------------------

        if (
            previous is not None
            and current is not None
        ):

            if current < previous:

                self.add_error(
                    "current_reading",
                    (
                        "Current reading cannot be lower "
                        "than the previous reading."
                    )
                )

        # ------------------------------------------------------
        # Equipment current reading
        # ------------------------------------------------------

        if (
            equipment
            and current is not None
            and not self.instance.pk
        ):

            equipment_hours = (
                equipment.current_hours
                or Decimal("0.0")
            )

            if current < equipment_hours:

                self.add_error(
                    "current_reading",
                    (
                        f"This equipment currently has "
                        f"{equipment_hours:.1f} hours. "
                        f"The new reading cannot be lower "
                        f"than the equipment's current reading."
                    )
                )

        # ------------------------------------------------------
        # Site consistency
        # ------------------------------------------------------

        if equipment and site:

            if (
                equipment.site_id
                and equipment.site_id != site.id
            ):

                self.add_error(
                    "site",
                    (
                        "The selected site does not match "
                        "the equipment's current operating site."
                    )
                )

        # ------------------------------------------------------
        # Prevent duplicate daily readings
        # ------------------------------------------------------

        if (
            equipment
            and reading_date
        ):

            duplicate = HourMeterReading.objects.filter(
                equipment=equipment,
                reading_date=reading_date,
            )

            if self.instance.pk:

                duplicate = duplicate.exclude(
                    pk=self.instance.pk
                )

            if duplicate.exists():

                self.add_error(
                    "reading_date",
                    (
                        "A reading already exists for this "
                        "equipment on this date."
                    )
                )

        return cleaned_data