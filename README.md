# Приложение для изучения английского языка

Это веб-приложение для изучения английского языка, которое позволяет пользователям:
- Проходить тесты на знание слов
- Создавать и управлять своими коллекциями слов
- Просматривать результаты тестов
- Добавлять новые слова и их переводы

## Основные функции
- **Тестирование:** Пользователи могут проходить тесты на знание слов. Тесты могут быть созданы из общедоступных или личных коллекций 
- **Коллекции слов:** Пользователи могут создавать коллекции слов, добавлять в них слова и управлять ими
- **Результаты тестов:** После прохождения теста пользователь может просмотреть свои результаты, включая точность ответов
- **Добавление слов:** Пользователи могут добавлять новые слова, переводы и их изображения в систему


## Используемые технологий

- Фронтенд:
  - React 
  - Material-UI (для стилизации и компонентов)
  - React Router (для маршрутизации)
  - Axios (для HTTP-запросов)

- Бэкенд:
  - Python
  - SQL Alchemy
  - FastAPI
  - Pydantic
  - Alembic для миграций

- База данных
  - PostgreSQL

- Инфраструктура:
  - Docker, Docker Compose
  - GitHub (для хранения кода)

## Как использовать
1. Регистрация и вход:
   - Зарегистрируйтесь или войдите в систему, чтобы получить доступ к полному функционалу приложения
2. Добавление слов:
   - Перейдите на страницу "Слова" и добавьте новые слова с их переводами
3. Создание коллекций:
   - На странице "Коллекции" создайте новую коллекцию и добавьте в неё слова
4. Прохождение тестов:
   - На странице "Тест" выберите коллекцию и начните тестирование
5. Просмотр результатов: 
   - После завершения теста вы можете просмотреть свои результаты на странице "Результаты"

## Установка и запуск

Предварительные требования
- Установите Docker и Docker Compose
- Убедитесь, что порты 8000 (бэкенд) и 3000 (фронтенд) свободны

Инструкции по запуску:
1. Клонируйте репозиторий бэкенда:
```
git clone https://github.com/mmikhail-git/english-test-backend.git
```

3. Клонируйте репозиторий фронтенда в соседнюю папку:
```
git clone https://github.com/mmikhail-git/english-test-frontend.git english-test-frontend
```

После этого структура папок должна выглядеть так:

```
  projects/
  ├── english-test-backend/
  │   ├── app/
  │   ├── docker-compose.yaml
  │   └── ...
  └── english-test-frontend/
      ├── src/
      ├── Dockerfile
      └── ...`
```

4. В папке english-test-backend создайте файл .env и добавьте в него необходимые переменные окружения (пример значений):
```
AUTH_KEY=76cf9af5c7ce008b1959755a37b2e795c96a77ab543064610d395244c54a8c10
DB_USER=postgres_user
DB_PASSWORD=postgres_password
DB_NAME=postgres_database
DB_HOST=db_3
DB_PORT=5432
```
Эти переменные используются в docker-compose.yaml для настройки бэкенда и базы данных.

5. Перейдите в папку english-test-backend
```
cd english-test-backend
```
6. Создайте Docker-сеть (если она еще не создана):
```
docker network create app3-network
```
7. Запустите сборку и запуск контейнеров с помощью Docker Compose:
```
docker-compose up --build -d
```

8.Выполните миграции БД
```
docker compose -f docker-compose.yml exec web alembic upgrade head
```

## Проверка работы приложения
1. После успешного запуска:
   - Бэкенд будет доступен по адресу: http://localhost:8000
   - Фронтенд будет доступен по адресу: http://localhost:3000
2. Проверьте, что оба сервиса работают корректно.

 Демо проекта доступно по ссылке - http://english.forb1.tech 

## Screenshots

![Screenshot 1](https://github.com/mmikhail-git/english-test-backend/blob/e44b238fe250ae8603f1e6dcaee03d8ae152c394/screenshots/screen1.png)
![Screenshot 2](https://github.com/mmikhail-git/english-test-backend/blob/e44b238fe250ae8603f1e6dcaee03d8ae152c394/screenshots/screen2.png)
![Screenshot 3](https://github.com/mmikhail-git/english-test-backend/blob/e44b238fe250ae8603f1e6dcaee03d8ae152c394/screenshots/screen3.png)
