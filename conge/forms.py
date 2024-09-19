from django import forms
from .models import Department, LeaveRequest, LeaveType
from django.core.exceptions import ValidationError
from datetime import date
from .models import ReligiousHoliday


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['type_conge', 'date_debut', 'date_fin', 'motif', ]
        labels = {
            'type_conge': 'Type de congé',
            'date_debut': 'Date de début',
            'date_fin': 'Date de fin',
            'motif': 'Motif'
        }
        widgets = {
            'type_conge': forms.Select(attrs={'class': 'form-select'}),
            'date_debut': forms.SelectDateWidget(
                years=range(2000, 2031),
                attrs={'class': 'form-select', 'placeholder': 'Choisissez une date'}
            ),
            'date_fin': forms.SelectDateWidget(
                years=range(2000, 2031),
                attrs={'class': 'form-select', 'placeholder': 'Choisissez une date'}
            ),
            'motif': forms.Textarea(
                attrs={'rows': 4, 'placeholder': 'Motif du congé', 'class': 'form-control'}
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type_conge'].queryset = LeaveType.objects.all()
        self.fields['date_debut'].widget.attrs.update({'class': 'form-control'})
        self.fields['date_fin'].widget.attrs.update({'class': 'form-control'})
        self.fields['motif'].widget.attrs.update({'class': 'form-control'})
        self.fields['type_conge'].widget.attrs.update({'class': 'form-control'})
    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')

        if date_debut and date_fin:
            if date_fin < date_debut:
                self.add_error('date_fin', 'La date de fin ne peut pas être antérieure à la date de début.')

        return cleaned_data



class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        labels = {
            'name': 'Nom du Département',
            'description': 'Description'
        }
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Nom du département'}
            ),
            'description': forms.Textarea(
                attrs={'rows': 3, 'placeholder': 'Description du département', 'class': 'form-control'}
            )
        }


class ReligiousHolidayForm(forms.ModelForm):
    class Meta:
        model = ReligiousHoliday
        fields = ['name', 'start_date', 'end_date']