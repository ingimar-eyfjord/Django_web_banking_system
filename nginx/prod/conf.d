upstream app_upstream {
    server app:8080;
}

server {
    listen 80;
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/ingimar.dk/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ingimar.dk/privkey.pem;

    server_name ingimar.dk www.ingimar.dk;

    location /static/ {
        alias /static/;
    }

    location /media/ {
        alias /media/;
    }

    location / {
        proxy_set_header Host $host;
        proxy_pass http://app_upstream;
        include uwsgi_params;
    }
}