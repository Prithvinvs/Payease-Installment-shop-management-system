# Deployment Guide

This guide details instructions for deploying the PayEase application to production environments.

---

## ☁️ Deploying to Render

Render is the recommended hosting platform for quick deployments.

### 1. Build Configurations
* **Service Type**: Web Service
* **Language**: Python
* **Build Command**: `pip install -r requirements.txt`
* **Start Command**: `gunicorn "app:create_app()" --bind 0.0.0.0:$PORT`

### 2. Environment Variables
Add the following key-value pairs in the Render console:
* `FLASK_APP`: `app.py`
* `FLASK_ENV`: `production`
* `SECRET_KEY`: `<generate-a-strong-random-key>`
* `SQLALCHEMY_DATABASE_URI`: `sqlite:///instance/store.db` (or a PostgreSQL URI)

---

## 🚂 Deploying to Railway

Railway automatically detects the `Procfile` and boots the server.

### 1. Deployment Steps
1. Connect your GitHub repository to Railway.
2. In variables, add `SECRET_KEY` and `FLASK_ENV=production`.
3. Railway will execute the `Procfile` commands:
   `web: gunicorn "app:create_app()" --bind 0.0.0.0:$PORT`

---

## 🐳 Containerized Deployments (Docker)

To deploy using Docker:

### 1. Build and Run Container
```bash
# Build the image
docker build -t instalment-shop-system .

# Run the container mapping ports and instance folders
docker run -d -p 5000:5000 \
  -v $(pwd)/instance:/app/instance \
  -v $(pwd)/backups:/app/backups \
  -e SECRET_KEY=strongkey123 \
  --name instalment-app instalment-shop-system
```

### 2. Docker Compose
Start the application and mount volumes automatically:
```bash
docker-compose up -d
```

---

## 🐧 Deploying to Ubuntu Server (Nginx + Gunicorn)

### 1. Install prerequisites
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx git -y
```

### 2. Clone and configure app
```bash
git clone <repo-url> /var/www/instalmentshop
cd /var/www/instalmentshop
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn
```

### 3. Create Systemd Service File
`sudo nano /etc/systemd/system/instalment.service`
```ini
[Unit]
Description=Gunicorn instance to serve PayEase app
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/instalmentshop
Environment="PATH=/var/www/instalmentshop/venv/bin"
ExecStart=/var/www/instalmentshop/venv/bin/gunicorn --workers 3 --bind unix:instalment.sock "app:create_app()"

[Install]
WantedBy=multi-user.target
```
Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl start instalment
sudo systemctl enable instalment
```

### 4. Configure Nginx Reverse Proxy
`sudo nano /etc/nginx/sites-available/instalment`
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/instalmentshop/instalment.sock;
    }
}
```
Link and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/instalment /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```
