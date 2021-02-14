from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import Blog

class CKEditorForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title' , 'content']
