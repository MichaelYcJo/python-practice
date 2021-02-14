from django import forms
from .models import FroalaPost
from froala_editor.widgets import FroalaEditor

class FroalaForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = FroalaPost
        widgets = {
            'content': FroalaEditor(options={
                'height': 600, 'width': '60%',
                'placeholderText': 'test',
            }),
            
        }