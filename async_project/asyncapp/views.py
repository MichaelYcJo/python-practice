from django.shortcuts import render, redirect
from .models import Subscriber, Article
from django.core.mail import send_mail
from django.conf import settings
from asgiref.sync import sync_to_async
import asyncio


# helper functino
async def async_send_mail(subject, message, email_list):
    print('현재 발송중')
    a_send_mail = sync_to_async(send_mail, thread_sensitive=False)
    await a_send_mail(subject, message, settings.EMAIL_HOST_USER, email_list, fail_silently=False)
    # uvicorn asyncproject.asgi.application -- reload
    print("메일발송 성공")


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
           async_send_mail(sub, msg, [email])
        )
        return redirect("/")


async def articlecreateview(request):
    if request.method == "GET":
        context = {
            "article_list": await sync_to_async(list)(Article.objects.all)()
        }
        return render(request, "articlecreate.html")
    else:
        title = request.POST.get("title")
        description = request.POST.get("description")
        await sync_to_async(Article.objects.create)(title=title, description=description)
        subject = "New Article uploaded"
        message = f"New Article with the title '{title}'"
        subscribers = await sync_to_async(list)(Subscriber.objects.all())
        email_list = [subscriber.email for subscriber in subscribers]

        asyncio.create_task(async_send_mail(subject, message, email_list))
        return redirect('asyncapp:home')