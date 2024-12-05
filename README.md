### Настройка nginx на сервере 
1. В конфигурации Nginx (/etc/nginx/sites-available/your_site.conf или аналогичном файле): 
    server {
    listen 80;
    server_name example.com;

    location /webhook/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
2. Проверяем что все работает:  sudo nginx -t

3. Перезагружаем nginx: sudo systemctl restart nginx

4. Проверяем что запросы доходят до контейнера: curl -X POST "http://127.0.0.1:8080" -d '{"test": "data"}'

