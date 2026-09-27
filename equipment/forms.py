from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Equipment
from companies.models import Site
from .models import ServiceRecord


class EquipmentForm(forms.ModelForm):

    class Meta:
        model = Equipment

        fields = [
            "company",
            "site",
            "asset_number",
            "name",
            "equipment_type",
            "manufacturer",
            "model",
            "serial_number",
            "registration_number",
            "year",
            "current_hours",
            "status",
            "image",
            "description",
            "purchase_date",
            "commissioning_date",
        ]

        widgets = {
            "company": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "site": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "asset_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. EXC-001",
                    "autocomplete": "off",
                }
            ),

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. CAT 320 Excavator",
                }
            ),

            "equipment_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "manufacturer": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Caterpillar",
                }
            ),

            "model": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 320D",
                }
            ),

            "serial_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Manufacturer serial number",
                }
            ),

            "registration_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Vehicle/equipment registration number",
                }
            ),

            "year": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 2024",
                    "min": 1900,
                    "max": timezone.now().year + 1,
                }
            ),

            "current_hours": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "0.0",
                    "step": "0.1",
                    "min": "0",
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/jpeg,image/png,image/webp",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Enter equipment description...",
                }
            ),

            "purchase_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "commissioning_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
        }

        labels = {
            "company": "Company",
            "site": "Operating Site",
            "asset_number": "Asset Number",
            "name": "Equipment Name",
            "equipment_type": "Equipment Type",
            "manufacturer": "Manufacturer",
            "model": "Model",
            "serial_number": "Serial Number",
            "registration_number": "Registration Number",
            "year": "Manufacturing Year",
            "current_hours": "Current Hour Meter",
            "status": "Equipment Status",
            "image": "Equipment Image",
            "description": "Description",
            "purchase_date": "Purchase Date",
            "commissioning_date": "Commissioning Date",
        }

        help_texts = {
            "asset_number": "Must be unique within the selected company.",
            "current_hours": "Enter the current accumulated operating hours.",
            "image": "JPG, PNG or WebP recommended.",
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # --------------------------------------------------
        # OPTIONAL FIELDS
        # --------------------------------------------------

        optional_fields = [
            "site",
            "manufacturer",
            "model",
            "serial_number",
            "registration_number",
            "year",
            "image",
            "description",
            "purchase_date",
            "commissioning_date",
        ]

        for field_name in optional_fields:
            self.fields[field_name].required = False


        # --------------------------------------------------
        # SITE DROPDOWN
        # --------------------------------------------------

        self.fields["site"].queryset = Site.objects.none()

        self.fields["site"].empty_label = "Select operating site"


        # --------------------------------------------------
        # CREATE / EDIT
        # --------------------------------------------------

        company = None

        # Editing an existing equipment record
        if self.instance and self.instance.pk:

            company = self.instance.company


        # Form was submitted
        if self.is_bound:

            company_id = self.data.get("company")

            if company_id:

                try:
                    company = self.instance.company.__class__.objects.get(
                        pk=company_id
                    )
                except company.__class__.DoesNotExist:
                    company = None

                except Exception:
                    company = None


        if company:

            self.fields["site"].queryset = Site.objects.filter(
                company=company,
                is_active=True,
            ).order_by("name")


    # ======================================================
    # ASSET NUMBER
    # ======================================================

    def clean_asset_number(self):

        asset_number = self.cleaned_data.get(
            "asset_number",
            ""
        ).strip()

        if not asset_number:

            raise ValidationError(
                "Asset number is required."
            )

        return asset_number.upper()


    # ======================================================
    # EQUIPMENT NAME
    # ======================================================

    def clean_name(self):

        name = self.cleaned_data.get(
            "name",
            ""
        ).strip()

        if not name:

            raise ValidationError(
                "Equipment name is required."
            )

        return name


    # ======================================================
    # MANUFACTURING YEAR
    # ======================================================

    def clean_year(self):

        year = self.cleaned_data.get("year")

        if year:

            current_year = timezone.now().year

            if year < 1900:

                raise ValidationError(
                    "Manufacturing year cannot be earlier than 1900."
                )

            if year > current_year + 1:

                raise ValidationError(
                    f"Manufacturing year cannot be later than "
                    f"{current_year + 1}."
                )

        return year


    # ======================================================
    # CURRENT HOURS
    # ======================================================

    def clean_current_hours(self):

        hours = self.cleaned_data.get(
            "current_hours"
        )

        if hours is not None and hours < 0:

            raise ValidationError(
                "Hour meter reading cannot be negative."
            )

        return hours


    # ======================================================
    # MAIN VALIDATION
    # ======================================================

    def clean(self):

        cleaned_data = super().clean()

        company = cleaned_data.get("company")
        site = cleaned_data.get("site")
        asset_number = cleaned_data.get("asset_number")

        # --------------------------------------------------
        # COMPANY + SITE VALIDATION
        # --------------------------------------------------

        if company and site:

            if site.company_id != company.id:

                self.add_error(
                    "site",
                    "The selected site does not belong to "
                    "the selected company."
                )


        # --------------------------------------------------
        # UNIQUE ASSET NUMBER
        # --------------------------------------------------

        if company and asset_number:

            qs = Equipment.objects.filter(
                company=company,
                asset_number__iexact=asset_number,
            )

            if self.instance and self.instance.pk:

                qs = qs.exclude(
                    pk=self.instance.pk
                )

            if qs.exists():

                self.add_error(
                    "asset_number",
                    "This asset number already exists "
                    "for this company."
                )


        # --------------------------------------------------
        # DATE VALIDATION
        # --------------------------------------------------

        purchase_date = cleaned_data.get(
            "purchase_date"
        )

        commissioning_date = cleaned_data.get(
            "commissioning_date"
        )

        if purchase_date and commissioning_date:

            if commissioning_date < purchase_date:

                self.add_error(
                    "commissioning_date",
                    "Commissioning date cannot be "
                    "earlier than the purchase date."
                )

        return cleaned_data



class ServiceRecordForm(forms.ModelForm):

    class Meta:
        model = ServiceRecord

        fields = [
            "equipment",
            "service_date",
            "service_type",
            "hour_meter_at_service",
            "service_interval",
            "air_filter_status",
            "notes",
        ]

        widgets = {

            "equipment": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "service_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "service_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "hour_meter_at_service": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                    "min": "0",
                    "placeholder": "e.g. 9809.0",
                }
            ),

            "service_interval": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                    "min": "0",
                    "placeholder": "e.g. 250.0",
                }
            ),

            "air_filter_status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Enter service notes...",
                }
            ),
        }

        labels = {
            "equipment": "Equipment",
            "service_date": "Service Date",
            "service_type": "Service Type",
            "hour_meter_at_service": "Hour Meter at Service",
            "service_interval": "Service Interval",
            "air_filter_status": "Air Filter",
            "notes": "Service Notes",
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["equipment"].queryset = (
            Equipment.objects
            .select_related(
                "company",
                "site",
            )
            .order_by(
                "asset_number"
            )
        )

    def clean_hour_meter_at_service(self):

        value = self.cleaned_data.get(
            "hour_meter_at_service"
        )

        if value is None:
            raise ValidationError(
                "Hour-meter reading is required."
            )

        if value < 0:
            raise ValidationError(
                "Hour-meter reading cannot be negative."
            )

        return value

    def clean_service_interval(self):

        value = self.cleaned_data.get(
            "service_interval"
        )

        if value is None:
            raise ValidationError(
                "Service interval is required."
            )

        if value <= 0:
            raise ValidationError(
                "Service interval must be greater than zero."
            )

        return value

    def clean(self):

        cleaned_data = super().clean()

        equipment = cleaned_data.get("equipment")
        hm = cleaned_data.get(
            "hour_meter_at_service"
        )

        if equipment and hm is not None:

            current_hm = equipment.current_hours or 0

            # Allow a new service record at or below
            # the current equipment hour meter.
            if hm > current_hm:

                self.add_error(
                    "hour_meter_at_service",
                    (
                        f"Service hour meter ({hm}) cannot be "
                        f"greater than the equipment's current "
                        f"hour meter ({current_hm}). "
                        "Update the equipment/hour-meter reading first."
                    ),
                )

        return cleaned_data



