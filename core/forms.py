from django import forms
from django.contrib.auth.models import User
from .models import Transaction, UserProfile

INPUT_STYLE = 'w-full h-12 px-4 rounded-xl border-slate-300 bg-slate-50 text-slate-700 placeholder-slate-400 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-all font-medium'
TEXTAREA_STYLE = 'w-full p-4 rounded-xl border-slate-300 bg-slate-50 text-slate-700 placeholder-slate-400 focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-all font-medium'


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

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['business_name', 'business_description']
        widgets = {
            'business_name': forms.TextInput(attrs={
                'class': INPUT_STYLE,
                'placeholder': 'Contoh: Seblak Janda Merana'
            }),
            'business_description': forms.Textarea(attrs={
                'class': TEXTAREA_STYLE,
                'rows': 4,
                'placeholder': 'Ceritakan model usahamu, contohnya Seblak Janda Merana'
            })
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email'] # Tambah email biar sekalian lengkap
        widgets = {
            'username': forms.TextInput(attrs={'class': INPUT_STYLE}),
            'email': forms.EmailInput(attrs={'class': INPUT_STYLE}),
        }