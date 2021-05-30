  
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import RedirectView

from article.models import Article
from like.models import LikeRecord


@method_decorator(login_required, 'get')
class LikeArticleView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('article:detail', kwargs={'pk': kwargs['pk']})

    def get(self, *args, **kwargs):

        user = self.request.user
        article = get_object_or_404(Article, pk=kwargs['pk'])

        try:
            messages.add_message(self.request, messages.SUCCESS, '좋아요가 반영되었습니다.')
        except ValidationError:
            messages.add_message(self.request, messages.ERROR, '좋아요는 한번만 가능합니다.')
            return HttpResponseRedirect(reverse('articleapp:detail', kwargs={'pk': kwargs['pk']}))

        return super(LikeArticleView, self).get(self.request, *args, **kwargs)