from django import forms
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