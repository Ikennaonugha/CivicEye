import math
from django import forms
from captcha.fields import CaptchaField
from .models import CivicFlag

# Maximum allowed upload size (5 MB)
MAX_UPLOAD_SIZE = 5 * 1024 * 1024
# Maximum allowed distance from project site for GPS verification (50 km)
MAX_ON_SITE_DISTANCE_KM = 50.0


class CivicFlagForm(forms.ModelForm):
    captcha = CaptchaField(
        label="Security Verification",
        help_text="Type the characters shown in the image above.",
    )

    class Meta:
        model = CivicFlag
        fields = [
            'issue_type',
            'headline',
            'description',
            'evidence_image',
            'user_latitude',
            'user_longitude',
        ]
        widgets = {
            'issue_type': forms.Select(attrs={'class': 'form-select'}),
            'headline': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'E.g., No active workers found at site',
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Provide details on what you observed...',
                }
            ),
            'evidence_image': forms.FileInput(attrs={'class': 'form-control'}),
            # Hidden fields populated via JavaScript geolocation
            'user_latitude': forms.HiddenInput(),
            'user_longitude': forms.HiddenInput(),
        }

    def __init__(self, *args, project=None, **kwargs):
        self.project = project
        super().__init__(*args, **kwargs)

    def clean_evidence_image(self):
        evidence_image = self.cleaned_data.get('evidence_image')
        if evidence_image and evidence_image.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError("Image size cannot exceed 5MB.")
        return evidence_image

    def clean_user_latitude(self):
        lat = self.cleaned_data.get('user_latitude')
        if lat is not None and (lat < -90.0 or lat > 90.0):
            raise forms.ValidationError("Latitude must be between -90 and 90 degrees.")
        return lat

    def clean_user_longitude(self):
        lng = self.cleaned_data.get('user_longitude')
        if lng is not None and (lng < -180.0 or lng > 180.0):
            raise forms.ValidationError("Longitude must be between -180 and 180 degrees.")
        return lng

    def clean(self):
        cleaned_data = super().clean()
        lat = cleaned_data.get('user_latitude')
        lng = cleaned_data.get('user_longitude')

        # Retrieve project reference from form init kwarg or model instance
        project = self.project or getattr(self.instance, 'project', None)

        if lat is not None and lng is not None and project:
            if project.latitude is not None and project.longitude is not None:
                # Calculate distance using Haversine formula
                r = 6371.0  # Earth radius in kilometers
                dlat = math.radians(lat - project.latitude)
                dlng = math.radians(lng - project.longitude)
                a = (
                    math.sin(dlat / 2) ** 2
                    + math.cos(math.radians(project.latitude))
                    * math.cos(math.radians(lat))
                    * math.sin(dlng / 2) ** 2
                )
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                distance_km = r * c

                if distance_km > MAX_ON_SITE_DISTANCE_KM:
                    raise forms.ValidationError(
                        f"Submitted GPS coordinates are too far from the project site ({distance_km:.1f} km away)."
                    )

        return cleaned_data