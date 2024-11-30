FROM python:3.13

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY --chown=appuser:appuser . /app/

USER appuser

CMD exec gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT
