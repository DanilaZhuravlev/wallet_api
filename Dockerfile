FROM python:3.12

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . /app/

# Открываем порт для веб-сервера Django
EXPOSE 8000

# Запускаем Gunicorn
CMD ["gunicorn", "--worker-class=gevent", "--workers=16", "--bind", "0.0.0.0:8000", "wallet_final.wsgi:application"]

