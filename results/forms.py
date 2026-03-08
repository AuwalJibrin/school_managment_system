from django import forms
from .models import Result

class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['student', 'subject', 'term', 'ca_score', 'exam_score']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'term': forms.Select(attrs={'class': 'form-select'}),
            'ca_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'exam_score': forms.NumberInput(attrs={'class': 'form-control'}),
        }
