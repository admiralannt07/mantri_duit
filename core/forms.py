from django import forms
from .models import Transaction

class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['receipt_image']
        widgets = {
            'receipt_image': forms.FileInput(attrs={
                'class': 'file-input file-input-bordered file-input-primary w-full max-w-xs',
                'accept': 'image/*'
            })
        }