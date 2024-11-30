FROM python:3.13

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/

CMD exec gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT
