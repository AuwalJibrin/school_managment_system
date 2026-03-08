from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Notification


class SignupForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    academic_document = forms.FileField(
        required=False,
        label="Academic Document (Required for Students)",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role', 'academic_document')

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        document = cleaned_data.get('academic_document')

        if role == 'student' and not document:
            self.add_error('academic_document', 'Students must upload an academic document for verification.')

        return cleaned_data

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'profile_image', 'academic_document')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'academic_document': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class StudentDocumentForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('academic_document',)
        widgets = {
            'academic_document': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class SendNotificationForm(forms.ModelForm):
    TARGET_CHOICES = (
        ('specific', 'Specific User'),
        ('students', 'All Students'),
        ('staff', 'All Staff'),
        ('all', 'All Users (Staff & Students)'),
    )

    target_group = forms.ChoiceField(
        choices=TARGET_CHOICES,
        initial='specific',
        label="Send To",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Notification
        fields = ('user', 'message')
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Type your message here...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.all()
        self.fields['user'].label = "Recipient"
        self.fields['user'].required = False

    def clean(self):
        cleaned_data = super().clean()
        target = cleaned_data.get('target_group')
        user = cleaned_data.get('user')

        if target == 'specific' and not user:
            raise forms.ValidationError("Please select a specific recipient.")
        
        return cleaned_data
