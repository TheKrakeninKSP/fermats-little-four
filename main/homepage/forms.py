from django import forms
from .models import Profile

class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_body_image']

from .models import ClothingUpload

class ClothingUploadForm(forms.ModelForm):
    class Meta:
        model = ClothingUpload
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
