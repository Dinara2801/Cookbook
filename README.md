[![Main Foodgram workflow](https://github.com/Dinara2801/tastyideas/actions/workflows/main.yml/badge.svg)](https://github.com/Dinara2801/tastyideas/actions/workflows/main.yml)

# Проект Tasyideas

Tasyideas — это сервис для создания, хранения и обмена рецептами. Позволяет пользователям создавать рецепты с ингредиентами и тегами, управлять ими, добавлять в избранное и в список покупок. Проект доступен по адресу https://tastyideas.sytes.net/

## Описание проекта

Проект представляет собой backend API для приложения рецептов. В основе — Django REST Framework с возможностью загрузки изображений, валидации ингредиентов и тегов, а также работы с пользователями.


## Основные функции
- Регистрация и аутентификация пользователей
- Подписка на авторов рецептов
- Создание, чтение, обновление и удаление рецептов
- Добавление ингредиентов и тегов к рецептам
- Загрузка и отображение изображений блюд
- Добавление рецептов в избранное и список покупок
- Возможность скачать список покупок

## Стек
- **Backend:** Django REST Framework
- **Frontend:** SPA (React)
- **Веб-сервер:** nginx
- **База данных:** PostgreSQL
- **Контейнеризация и CI/CD:** Docker, GitHub Actions

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Dinara2801/foodgram.git
```

```
cd backend
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Заполнить базу данных: 
 
``` 
python manage.py import_data 
``` 

Запустить проект:

```
python3 manage.py runserver
```

Для фронтенда:

```
cd ../frontend
npm install
npm start
```

## Пример файла .env

```
SECRET_KEY=ваш_секретный_ключ
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DJANGO_DB_ENGINE=postgresql
POSTGRES_DB=foodgram_db
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=пароль

DB_HOST=localhost
DB_PORT=5432

CSV_DATA_PATH=develop
```

## Автор

**Махмутова Динара**

GitHub: https://github.com/Dinara2801
