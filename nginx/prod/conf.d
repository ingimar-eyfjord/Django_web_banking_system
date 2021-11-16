upstream app_upstream {
    server app:8080;
}

server {
    listen 80;
    listen 443;
    ssl on;
    ssl_certificate /etc/letsencrypt/live/stroem.xyz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/stroem.xyz/privkey.pem;

    server_name stroem.xyz;

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