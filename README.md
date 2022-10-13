# «Продуктовый помощник»  
  
 На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.  
   
 

## Стек технологий:

 Python 
 Django
 Django Rest Framework
 PosgreSQL
 Docker
 
 *Более подробно об используемых технологиях и их версиях смотрите в requirements.txt*

## Данные для тестирования проекта на боевом сервере:

http://zrivkoren.ddns.net/recipes


## Запуск проекта

### Запуск проекта локально

1.  Клонировать репозиторий и перейти в него

`git@github.com:zrivkoren/foodgram-project-react.git`

2.  Создать и активировать виртуальное окружение

`python -m venv env`

`env/Scripts/activate`

3.  Обновить pip и установить зависимости

`python -m pip install --upgrade pip`

`pip install -r requirements.txt`

4.  Выполнить миграции и создать суперпользователя

`python manage.py makemigrations`

`python manage.py migrate`

`python manage.py createsuperuser`

5.  Запустить сервер

`python manage.py runserver`

6.  Для запуска фронтенда через терминал перейти в папку где хранится проект и найти папку "infra"

7.  Собрать контейнер

`docker-compose up --build`

### Запуск проекта на удаленном сервере

1.  Выполните вход на свой удаленный сервер
    
2.  Установите docker на сервер:
        

> подробная инструкция на https://docs.docker.com/engine/install/ubuntu/

    
3.  Установите docker-compose на сервер:
    

> инструкция по адресу https://docs.docker.com/compose/install/

4.  Отредактируйте файл infra/nginx.conf и в строке server_name впишите свой IP
    
5.  Скопируйте файлы docker-compose.yml и nginx.conf из директории infra на сервер:
    

`scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml` `scp nginx.conf <username>@<host>:/home/<username>/nginx.conf`

6.  Cоздайте .env файл и впишите:
    
    ```
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<имя базы данных postgres>
    POSTGRES_USER=<пользователь бд>
    POSTGRES_PASSWORD=<пароль>
    DB_HOST=<db>
    DB_PORT=<5432>
    SECRET_KEY=<секретный ключ проекта django>
    ALLOWED_HOSTS=[]<разрешенные хосты>
    DEBUG=<0 или 1>    
    
    ```  

    
7.  На сервере соберите docker-compose:
    

`sudo docker-compose up -d --build`

8.  После успешной сборки на сервере выполните команды:

-   Соберите статические файлы:

```
`sudo docker-compose exec web python manage.py collectstatic --noinput`

```

-   Примените миграции:

    sudo docker-compose exec web python manage.py makemigrations
    sudo docker-compose exec web python manage.py migrate  

Загрузите ингредиенты в базу данных (необязательно):

`sudo docker-compose exec web python manage.py loaddata ingredientsN.json`


-   Создайте суперпользователя Django:


`  sudo docker-compose exec web python manage.py createsuperuser`

```

-   Проект будет доступен по вашему IP
