from django import forms

class ContactForm(forms.Form):
    fullName = forms.CharField(
        label="Full Name*",
        widget=forms.TextInput(attrs={'placeholder': 'John Doe'})
    )
    email = forms.EmailField(
        label="Email*",
        widget=forms.EmailInput(attrs={'placeholder': 'example@yourmail.com'})
    )
    phone = forms.CharField(
        label="Phone*",
        widget=forms.TextInput(attrs={'placeholder': '+234 803 123 4567'})
    )
    message = forms.CharField(
        label="Message*",
        widget=forms.Textarea(attrs={'rows': 1, 'placeholder': 'type your message here'})
    )