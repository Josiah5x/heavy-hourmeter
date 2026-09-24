from django import forms
from django.core.exceptions import ValidationError

from .models import Company, Site


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company

        fields = [
            "name",
            "short_name",
            "address",
            "phone",
            "email",
            "website",
            "logo",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter company name",
            }),

            "short_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. ABC Ltd",
            }),

            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Company address",
            }),

            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "+234...",
            }),

            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "company@example.com",
            }),

            "website": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://example.com",
            }),

            "logo": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": "image/*",
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()

        if not name:
            raise ValidationError("Company name is required.")

        qs = Company.objects.filter(name__iexact=name)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError(
                "A company with this name already exists."
            )

        return name

    def clean_short_name(self):
        short_name = self.cleaned_data.get("short_name", "").strip()

        if short_name:
            qs = Company.objects.filter(
                short_name__iexact=short_name
            )

            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise ValidationError(
                    "This short name is already being used."
                )

        return short_name


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site

        fields = [
            "company",
            "name",
            "code",
            "address",
            "city",
            "state",
            "country",
            "contact_person",
            "contact_phone",
            "latitude",
            "longitude",
            "is_active",
        ]

        widgets = {
            "company": forms.Select(attrs={
                "class": "form-select",
            }),

            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Abuja Construction Site",
            }),

            "code": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. SITE-001",
            }),

            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Site address",
            }),

            "city": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Abuja",
            }),

            "state": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. FCT",
            }),

            "country": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nigeria",
            }),

            "contact_person": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Site contact person",
            }),

            "contact_phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "+234...",
            }),

            "latitude": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. 9.0765",
                "step": "any",
            }),

            "longitude": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. 7.3986",
                "step": "any",
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["company"].queryset = Company.objects.filter(
            is_active=True
        ).order_by("name")

    def clean_name(self):
        name = self.cleaned_data["name"].strip()

        if not name:
            raise ValidationError("Site name is required.")

        company = self.cleaned_data.get("company")

        if company:
            qs = Site.objects.filter(
                company=company,
                name__iexact=name,
            )

            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise ValidationError(
                    "This company already has a site with this name."
                )

        return name

    def clean_code(self):
        code = self.cleaned_data.get("code", "").strip()

        if code:
            code = code.upper()

            company = self.cleaned_data.get("company")

            if company:
                qs = Site.objects.filter(
                    company=company,
                    code__iexact=code,
                )

                if self.instance.pk:
                    qs = qs.exclude(pk=self.instance.pk)

                if qs.exists():
                    raise ValidationError(
                        "This site code is already used by this company."
                    )

        return code

    def clean(self):
        cleaned_data = super().clean()

        latitude = cleaned_data.get("latitude")
        longitude = cleaned_data.get("longitude")

        if latitude is not None:
            if latitude < -90 or latitude > 90:
                self.add_error(
                    "latitude",
                    "Latitude must be between -90 and 90."
                )

        if longitude is not None:
            if longitude < -180 or longitude > 180:
                self.add_error(
                    "longitude",
                    "Longitude must be between -180 and 180."
                )

        return cleaned_data