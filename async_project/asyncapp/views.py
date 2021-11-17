from django.shortcuts import render, redirect
from .models import Subscriber, Article
from django.core.mail import send_mail
from django.conf import settings
from asgiref.sync import sync_to_async
import asyncio


async def homeview(request):
    if request.method == "GET":
        context = {}
        return render(request, 'home.html', context)
    else:
        email = request.POST.get('email')
        await sync_to_async(Subscriber.objects.create)(email=email)
        sub = "Subscription successful"
        msg = f"Hello {email}, Thanks for subscribing us. Noew you will get email"

        a_send_mail = sync_to_async(send_mail)
        asyncio.create_task(
            a_send_mail(sub, msg, settings.EMAIL_HOST_USER, [email], fail_silently=False)
        )
        return redirect("/")