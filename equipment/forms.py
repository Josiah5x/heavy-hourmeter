from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Equipment
from companies.models import Site


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
                    "accept": "image/*",
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
            "image": "Recommended formats: JPG, JPEG or PNG.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make optional fields explicit
        self.fields["site"].required = False
        self.fields["manufacturer"].required = False
        self.fields["model"].required = False
        self.fields["serial_number"].required = False
        self.fields["registration_number"].required = False
        self.fields["year"].required = False
        self.fields["image"].required = False
        self.fields["description"].required = False
        self.fields["purchase_date"].required = False
        self.fields["commissioning_date"].required = False

        # Better empty option
        self.fields["site"].empty_label = "Select operating site"

    def clean_asset_number(self):
        asset_number = self.cleaned_data.get("asset_number", "").strip()

        if not asset_number:
            raise ValidationError("Asset number is required.")

        return asset_number.upper()

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()

        if not name:
            raise ValidationError("Equipment name is required.")

        return name

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
                    f"Manufacturing year cannot be later than {current_year + 1}."
                )

        return year

    def clean_current_hours(self):
        hours = self.cleaned_data.get("current_hours")

        if hours is not None and hours < 0:
            raise ValidationError(
                "Hour meter reading cannot be negative."
            )

        return hours

    def clean(self):
        cleaned_data = super().clean()

        company = cleaned_data.get("company")
        asset_number = cleaned_data.get("asset_number")

        if company and asset_number:
            qs = Equipment.objects.filter(
                company=company,
                asset_number__iexact=asset_number,
            )

            # Don't treat the current object as a duplicate during editing.
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                self.add_error(
                    "asset_number",
                    "This asset number already exists for this company.",
                )

        purchase_date = cleaned_data.get("purchase_date")
        commissioning_date = cleaned_data.get("commissioning_date")

        if purchase_date and commissioning_date:
            if commissioning_date < purchase_date:
                self.add_error(
                    "commissioning_date",
                    "Commissioning date cannot be earlier than the purchase date.",
                )

        return cleaned_data