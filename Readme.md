### Instructions

1. python manage.py runserver 9000
2. run redis
    ```
    sudo systemctl start redis-server
    redis-cli
    ```
3. run celery
    ```
    celery -A The_Wow worker -l info
    ```