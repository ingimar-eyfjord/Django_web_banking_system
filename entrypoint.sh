#!/bin/sh

echo "${RTE} Runtime Environment - Running entrypoint."

if [ "$RTE" = "dev" ]; then

    python manage.py makemigrations --merge
    python manage.py migrate --noinput
    python manage.py runserver "$APP_IP_SCOPE":8000

elif [ "$RTE" = "test" ]; then

    echo "This is tets."

elif [ "$RTE" = "prod" ]; then

    python manage.py check --deploy
    python manage.py collectstatic --noinput
    gunicorn kea_bank.asgi:application -b 0.0.0.0:8080 -k uvicorn.workers.UvicornWorker

fi