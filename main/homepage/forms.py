from django import forms
from .models import Profile

class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_body_image']
