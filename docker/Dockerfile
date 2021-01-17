FROM python:3.8.2-buster

RUN apt-get update && apt-get install -y --no-install-recommends
RUN apt-get install -y locales locales-all

RUN mkdir -p /app
COPY ./src/cinemabot /app

RUN pip install -r /app/requirements.txt

ENV LANG ru_RU.UTF-8
ENV LANGUAGE ru_RU.UTF-8
ENV PYTHONIOENCODING utf-8
ENV LC_ALL ru_RU.UTF-8
ENV LC_CTYPE ru_RU.UTF-8
RUN dpkg-reconfigure locales

CMD ["python", "/app/cinemabot/bot.py"]