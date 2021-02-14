from django import forms
from django.forms.widgets import TextInput
from .models import Tinynote
from tinymce.widgets import TinyMCE

class TinyForm(forms.ModelForm):

    class Meta:
        model = Tinynote
        fields= ('title', 'content',)
        widgets = {
            'title' : TextInput(attrs={'class': 'form-control', 'placeholder': 'Page Title'}),
            'content' : TinyMCE(attrs={'cols': 80, 'rows': 30,'class': 'form-control'}),
        }