# Dockerfile
FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY ./ /app
COPY requirements.txt /app/

RUN pip install --upgrade pip \
 && pip install -r requirements.txt

CMD ["gunicorn", "ecom.wsgi:application", "--bind", "0.0.0.0:8000"]
