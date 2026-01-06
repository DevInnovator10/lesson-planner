from django import forms
from .models import Document, Tag, Philosophy, Persona, Voice, Tone

class DocumentUploadForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'select2-multiple',
            'data-placeholder': 'Select tags...'
        }),
        required=False
    )

    class Meta:
        model = Document
        fields = ['file', 'tags']


MODEL_CHOICES = [
    ('gpt-4o-mini-2024-07-18', 'GPT-4o Mini (Default)'),
    ('gpt-4o-2024-08-06', 'GPT-4o'),
    ('gpt-4-turbo-2024-04-09', 'GPT-4 Turbo'),
    
]

class SearchForm(forms.Form):
    query = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True)
    philosophy = forms.ModelChoiceField(queryset=Philosophy.objects.all(), required=False)
    personas = forms.ModelMultipleChoiceField(queryset=Persona.objects.all(), required=False)
    voice = forms.ModelChoiceField(queryset=Voice.objects.all(), required=False)
    tone = forms.ModelMultipleChoiceField(queryset=Tone.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)
    model = forms.ChoiceField(choices=MODEL_CHOICES, required=False, initial='gpt-4o-mini-2024-07-18')
