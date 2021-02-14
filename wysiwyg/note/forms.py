from django import forms
from .models import Post
#CKEditor, QuillPost, FroalaPost
from django_summernote.widgets import SummernoteWidget
#from froala_editor.widgets import FroalaEditor


class SummerNoteForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {
            'content': SummernoteWidget(),
        }

'''

    

class QuillPostForm(forms.ModelForm):
    class Meta:
        model = QuillPost
        fields = (
            'title', 'content',
        )


'''