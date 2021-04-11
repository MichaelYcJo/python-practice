FROM python:3.8.5-alpine


RUN echo "testing1123124"

RUN pip install --upgrade pip

# COPY명령어를 사용하여 이전에 만든 파일을 이미지에 복사
# COPY <복사할 파일 경로> <이미지에서 파일이 위치할 경로>
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./django_project /app

WORKDIR /app

COPY ./entrypoint.sh /
# ENTRYPOINT는 컨테이너가 시작되었을 때 스크립트 혹은 명령을 실행
ENTRYPOINT ["sh", "/entrypoint.sh"]


#  파이썬 버퍼를 1로 설정, 응용프로그램 출력 실시간 출력이 가능해짐
#ENV PYTHONUNBUFFERED 1


