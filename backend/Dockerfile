FROM python:3.9
WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY data ./data
COPY backend ./backend

WORKDIR /app/backend

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram_backend.wsgi"]