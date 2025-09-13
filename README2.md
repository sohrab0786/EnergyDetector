 EnergyDetector - Cool Roof Calculator

This project is a Django-based web application that uses **EnergyPlus** for energy simulations. It leverages **Celery** for background task processing and **Gunicorn** for serving the Django app. This guide explains how to deploy and keep the application running **forever** on an AWS EC2 instance.

---

## 1. Prerequisites

- Ubuntu 20.04/22.04 (EC2 instance)
- Python 3.8+
- Virtualenv
- EnergyPlus installed (`/usr/local/bin/energyplus`)
- RabbitMQ or Redis (for Celery broker)
- EC2 Security Group rules:
  - HTTP (TCP 80)
  - HTTPS (TCP 443)
  - SSH (TCP 22)
  - Custom TCP if testing other ports (e.g., 8000)

---

## 2. Clone the Project

```bash
git clone https://github.com/sohrab0786/EnergyDetector.git
cd EnergyDetector
##3. Setup Python Environment

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
4. Configure Django Settings
##Update settings.py:

##ALLOWED_HOSTS → EC2 public IP or domain

##STATICFILES_DIRS and STATIC_ROOT

##Celery broker URL (BROKER_URL) for RabbitMQ/Redis

##5. Database Migration
python manage.py migrate
python manage.py collectstatic
##6. Test Locally

python manage.py runserver 0.0.0.0:8000
##Visit http://<EC2_PUBLIC_IP>:8000 to ensure the frontend is working.

##7. Systemd Service for Gunicorn
##Create /etc/systemd/system/energydetector-gunicorn.service:


[Unit]
Description=Gunicorn instance for EnergyDetector
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/EnergyDetector
Environment="PATH=/home/ubuntu/EnergyDetector/venv/bin"
ExecStart=/home/ubuntu/EnergyDetector/venv/bin/gunicorn CoolRoof.wsgi:application --workers 3 --bind 0.0.0.0:80

[Install]
WantedBy=multi-user.target
Start and enable Gunicorn:


sudo systemctl daemon-reload
sudo systemctl start energydetector-gunicorn
sudo systemctl enable energydetector-gunicorn
sudo systemctl status energydetector-gunicorn
##8. Systemd Service for Celery
##Create /etc/systemd/system/energydetector-celery.service:


[Unit]
Description=Celery Worker for EnergyDetector
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/EnergyDetector
Environment="PATH=/home/ubuntu/EnergyDetector/venv/bin"
ExecStart=/home/ubuntu/EnergyDetector/venv/bin/celery -A CoolRoof worker --loglevel=info

[Install]
WantedBy=multi-user.target
Start and enable Celery:


sudo systemctl daemon-reload
sudo systemctl start energydetector-celery
sudo systemctl enable energydetector-celery
sudo systemctl status energydetector-celery
##9. Security Group / Firewall
##Ensure EC2 Security Group allows:

##TCP 80 (HTTP)

##TCP 443 (HTTPS)

##TCP 22 (SSH)

##If testing Gunicorn on 8000, allow TCP 8000 as well.

##10. Logs
##Gunicorn logs:


journalctl -u energydetector-gunicorn -f
##Celery logs:


sudo tail -f /var/log/celery.out.log /var/log/celery.err.log
##11. Updating Code

cd ~/EnergyDetector
git pull origin main
source venv/bin/activate

# Restart services
sudo systemctl restart energydetector-gunicorn
sudo systemctl restart energydetector-celery
##12. Troubleshooting
##Celery tasks not running:

##Check Celery logs

##Confirm RabbitMQ/Redis broker is running

##Port 80 in use error:


sudo lsof -i :80
sudo kill -9 <PID>
sudo systemctl restart energydetector-gunicorn
Frontend live but simulations hang:

Confirm energyplus path (which energyplus)

Monitor Celery logs

Ensure /tmp and output directories are writable

13. Quick Commands

# Restart services
sudo systemctl restart energydetector-gunicorn
sudo systemctl restart energydetector-celery

# Enable services at boot
sudo systemctl enable energydetector-gunicorn
sudo systemctl enable energydetector-celery

# Check service status
sudo systemctl status energydetector-gunicorn
sudo systemctl status energydetector-celery

##Later if stops then stop and start instance Cool Roof Calculator
##then connect the instance it will give terminal then run below commands
sudo systemctl daemon-reload
sudo systemctl enable energydetector-gunicorn
sudo systemctl enable energydetector-celery
sudo systemctl start energydetector-gunicorn
sudo systemctl start energydetector-celery
enable → ensures services start automatically after EC2 reboot.
start → starts them immediately.

4. Verify

sudo systemctl status energydetector-gunicorn
sudo systemctl status energydetector-celery
#check the public address then ex- 35.154.18.185  then search this url on web - http://35.154.18.185:8000/CoolRoof/
Author: Md Sohrab Emam
Project: EnergyDetector - Cool Roof Calculator
