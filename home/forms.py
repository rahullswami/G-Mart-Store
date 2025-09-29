from django import forms
from .models import SellerProfile
from .models import Review

class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ['store_name', 'brand_image']




class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Email'
        })
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Your Message',
            'rows': 5
        })
    )


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Share your experience with this product...'
            }),
        }
    
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not rating:
            raise forms.ValidationError('Please select a rating')
        return rating