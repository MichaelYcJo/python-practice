from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    content = forms.CharField(label='', widget=forms.TextInput(attrs={
        'class': 'comment-form',
        'size': '70px',
        'placeholder': '댓글 달기...',
        'maxlength': '40', }))
    
    class Meta:
        model = Comment
        fields = ['content']
        