FROM python:3.9.0

RUN mkdir /root/.ssh/

# 이미지를 가지는 사람도 private key입수가 가능하다는 점을 명심
ADD ./ssh/id_rsa/ root/.ssh/id_rsa

# 권한부여
RUN chmod 600 /riit/.ssh/id_rsa

# 깃허브를 ssh에 등록하기 위한 작업
RUN touch /root/.ssh/known_hosts

RUN ssh-keyscan github.com >> /root/.ssh/known_hosts 

WORKDIR /home/

RUN echo "testing1123124"

RUN git clone https://github.com/michael-cho77/django-pinterest.git

WORKDIR /home/django-pinterest/

RUN pip install -r requirements.txt

# 뒤에 추가되었기때문에 따로 추가해주어야함
RUN pip install gunicorn

RUN pip install mysqlclient

EXPOSE 8000

CMD ["bash", "-c", "python manage.py collectstatic --noinput --settings=config.settings.deploy && python manage.py migrate --settings=config.settings.deploy && gunicorn config.wsgi --env DJANGO_SETTINGS_MODULE=config.settings.deploy --bind 0.0.0.0:8000"]

#CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0:8000"]
#CMD ["python", "manage.py", "runserver", "0.0.0:8000"]