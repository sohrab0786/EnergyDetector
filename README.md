
# 🔋 EnergyDetector

EnergyDetector is a Django-based application that simulates home energy usage based on user-provided parameters.  
It integrates with **EnergyPlus v8.9.0** to run energy consumption simulations and provides results through a web interface.

---

## 📌 Features
- Input home details through a simple form.
- Simulate energy usage with **EnergyPlus**.
- View detailed energy consumption results.
- Fully configurable EnergyPlus path for flexibility.

---

## 📦 Prerequisites

Before setting up, make sure you have:
- **Python 3.7+**
- **EnergyPlus v8.9.0** installed ([Download here](https://energyplus.net/downloads))
- Git installed

---

## ⚙️ Installation & Setup

1️⃣ **Clone the repository**
```bash
git clone https://github.com/sohrab0786/EnergyDetector.git
cd EnergyDetector

sudo apt update
sudo apt install python3.12-venv -y

#install energyplus
wget https://github.com/NREL/EnergyPlus/releases/download/v8.9.0/EnergyPlus-8.9.0-40101eaafd-Linux-x86_64.sh
chmod +x EnergyPlus-8.9.0-40101eaafd-Linux-x86_64.sh
sudo ./EnergyPlus-8.9.0-40101eaafd-Linux-x86_64.sh
echo 'export PATH=$PATH:/usr/local/EnergyPlus-8-9-0' >> ~/.bashrc
source ~/.bashrc
energyplus --version

2️⃣ Create and activate a virtual environment
python -m venv venv
# Activate on Windows
venv\Scripts\activate
# Activate on macOS/Linux
source venv/bin/activate

# CoolRoof Django Project Deployment Guide

This guide explains how to deploy, run, and maintain the **CoolRoof** Django project with Celery workers, Gunicorn, Nginx, and HTTPS on an **Ubuntu EC2 instance**.  

---

## **1. Connect to your EC2 instance**
```bash
ssh -i path/to/your-key.pem ubuntu@your-ec2-ip or select instance then click connect button to connect using aws terminal.
cd ~/EnergyDetector
source venv310/bin/activate
2. Database migrations
Make sure your database and Django apps are migrated properly.

python manage.py makemigrations
python manage.py migrate
If you need to reset django_celery_results:

python manage.py migrate django_celery_results zero
python manage.py migrate django_celery_results
3. Install and start Celery worker as a service
Create a systemd service for Celery:


sudo nano /etc/systemd/system/coolroof-celery.service
Paste this:

#-------------------------------------------------------------
[Unit]
Description=Celery Worker for CoolRoof Django project
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/EnergyDetector
Environment="PATH=/home/ubuntu/EnergyDetector/venv310/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/ubuntu/EnergyDetector/venv310/bin/celery -A CoolRoof worker --loglevel=info

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
Reload systemd, start, and enable the service:

#-----------------------------------------------------------------
#then ctr+o to save and ctrl+x to exit then run below command.

sudo systemctl daemon-reload
sudo systemctl start coolroof-celery
sudo systemctl enable coolroof-celery
sudo systemctl status coolroof-celery
Check logs if needed:

sudo journalctl -u coolroof-celery -f
4. Install Gunicorn

pip install gunicorn
Run manually (for testing):


gunicorn CoolRoof.wsgi:application --bind 0.0.0.0:8000
5. Configure Gunicorn as a systemd service

sudo nano /etc/systemd/system/coolroof-gunicorn.service
Paste this:
#---------------------------------------
[Unit]
Description=Gunicorn instance to serve CoolRoof
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/EnergyDetector
Environment="PATH=/home/ubuntu/EnergyDetector/venv310/bin"
ExecStart=/home/ubuntu/EnergyDetector/venv310/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 CoolRoof.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target

#---------------------------------------
Reload systemd, start, and enable: ctrl+o and ctrl+x

#run below command
sudo systemctl daemon-reload
sudo systemctl start coolroof-gunicorn
sudo systemctl enable coolroof-gunicorn
sudo systemctl status coolroof-gunicorn

6. Install and configure Nginx

sudo apt update
sudo apt install nginx -y
Create Nginx site config:

sudo nano /etc/nginx/sites-available/coolroof
Add:

#----------------------------------------------
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/ubuntu/EnergyDetector;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
#---------------------------------------
Enable the site and restart Nginx: ctrl+o and ctrl+x


sudo ln -s /etc/nginx/sites-available/coolroof /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
7. Setup HTTPS with Let’s Encrypt
Install Certbot:

sudo apt install certbot python3-certbot-nginx -y
Run Certbot:


sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
Follow the prompts to get an HTTPS certificate.

Check automatic renewal:

sudo systemctl status certbot.timer
8. Configure Environment Variables
Make sure the Django settings.py has:

DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
9. Running the project
After setup, the following services will always run:

Celery worker: sudo systemctl status coolroof-celery

Gunicorn server: sudo systemctl status coolroof-gunicorn

Nginx: sudo systemctl status nginx

To restart any service:

sudo systemctl restart coolroof-celery
sudo systemctl restart coolroof-gunicorn
sudo systemctl restart nginx
10. Troubleshooting
Static files not loading:
Run:

python manage.py collectstatic
Celery FileNotFoundError (EnergyPlus):
Make sure the path is correct in your tasks.py:


ENERGYPLUS_PATH = "/usr/local/bin/energyplus"
And subprocess uses full path:

subprocess.Popen([ENERGYPLUS_PATH, ...])
Logs:

Gunicorn: sudo journalctl -u coolroof-gunicorn -f

Celery: sudo journalctl -u coolroof-celery -f

Nginx: /var/log/nginx/error.log

✅ Notes
All services are enabled to start at boot.

HTTPS is set up with automatic renewal.

Full paths should be used for any external binaries (like EnergyPlus) in Celery tasks.

Your site should now be live at: https://yourdomain.com

