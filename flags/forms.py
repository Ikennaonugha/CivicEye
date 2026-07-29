from django import forms
from captcha.fields import CaptchaField
from .models import CivicFlag

# Maximum allowed upload size (5 MB)
MAX_UPLOAD_SIZE = 5 * 1024 * 1024


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

    def clean_evidence_image(self):
        evidence_image = self.cleaned_data.get('evidence_image')
        if evidence_image and evidence_image.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError("Image size cannot exceed 5MB.")
        return evidence_image