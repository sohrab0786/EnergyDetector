Here’s a step-by-step plan to run the EnergyDetector project with Celery + Django + EnergyPlus 8.9 on an AWS EC2 instance. I’ll include both a general plan and some concrete commands you might use (assuming a Ubuntu-based EC2). Happy to adjust if your OS or requirements differ.

What we need to verify / assumptions

Before setting up, check / decide:

What OS your EC2 instance will run (Ubuntu 20.04 / 22.04, Amazon Linux, etc.).

Do you have root / sudo privileges.

Whether Celery will use Redis or RabbitMQ as broker.

If you want the DB (Django) to use SQLite (as in the project currently) or something more production-ready (PostgreSQL / MySQL).

Whether you want to run everything on one EC2 or split components (web server, worker, broker) on separate machines.

Ensure EnergyPlus 8.9 binaries are available for the OS you have. (Project requires EnergyPlus v8.9.0). 
GitHub

High-level architecture

Something like:

EC2 instance
 ├ Django web server (Gunicorn / uvicorn + nginx)
 ├ Celery worker(s)
 ├ Broker (Redis / RabbitMQ)
 ├ EnergyPlus installed to run simulation
 └ Database (could be on the same or external)

Detailed steps

Here’s how you might set this up.

1. Provision EC2 instance

Launch an EC2 instance, e.g., Ubuntu 22.04, with enough CPU/RAM (since simulations may be heavy).

Open necessary security group ports: 22 (SSH), 80/443 (HTTP/HTTPS), maybe 8000 for testing.

If using Redis / RabbitMQ on same instance, ensure appropriate ports (but prefer local binding).

2. Install system dependencies

SSH in, then run something like:

sudo apt update
sudo apt install -y python3 python3-venv python3-pip git build-essential wget unzip


Also dependencies for EnergyPlus (some libs may be needed).

3. Install EnergyPlus v8.9

You need to download the EnergyPlus v8.9 installer for Linux. If there is a .sh version or tarball.

Download the EnergyPlus 8.9 for Linux from official site. 
energyplus.net
+1

Make it executable, run installation.

Example:

wget https://big_download_link/EnergyPlus-8.9.0-<...>-Linux-x86_64.sh   # fill actual url
chmod +x EnergyPlus-8.9.0-*.sh
sudo ./EnergyPlus-8.9.0-*.sh


During installation it may prompt for license / directories.

After installation, it typically goes under /usr/local/EnergyPlus-8.9.0 or similar.

Ensure the energyplus executable is in your PATH or you know the full path.

You may need to install some supporting libs if errors occur.

4. Clone the EnergyDetector project
cd /home/ubuntu
git clone https://github.com/sohrab0786/EnergyDetector.git
cd EnergyDetector

5. Python environment & dependencies
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt


Make adjustments if any package fails (e.g. dependency needing system-lib).

6. Configure EnergyPlus path in the project

In the project, there is a setting (in Calculator/tasks.py) for ENERGYPLUS_PATH which defaults to a Windows path. 
GitHub

Modify it to point to the Linux path where EnergyPlus executable resides, e.g.:

ENERGYPLUS_PATH = "/usr/local/EnergyPlus-8.9.0/energyplus"


You might also need to ensure the project has permission to execute that file.

7. Setup database & Django settings

If staying with SQLite for testing, fine. But for more reliability, setup PostgreSQL:

sudo apt install -y postgresql libpq-dev
# create DB, user
sudo -u postgres psql
> CREATE DATABASE energydetector;
> CREATE USER energyuser WITH PASSWORD 'password';
> GRANT ALL PRIVILEGES ON DATABASE energydetector TO energyuser;


In Django settings, set up DATABASES accordingly.

Run migrations:

python manage.py migrate

8. Setup Celery

Decide on broker: e.g. install Redis

sudo apt install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server


In Django settings (or wherever Celery config is), set CELERY_BROKER_URL to redis://localhost:6379/0 (or RabbitMQ if using).

Install Celery in the project (already in requirements, hopefully).

Create a systemd service or supervisor to run Celery worker (and Celery beat if needed) so that they start on boot and restart on failure.

Example systemd unit file /etc/systemd/system/energydetector-celery.service:

[Unit]
Description=Celery Worker for EnergyDetector
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/EnergyDetector
Environment="PATH=/home/ubuntu/EnergyDetector/venv/bin"
ExecStart=/home/ubuntu/EnergyDetector/venv/bin/celery -A EnergyDetector worker --loglevel=info

Restart=always

[Install]
WantedBy=multi-user.target


Similarly for celerybeat if the project uses periodic tasks.

9. Setup the web server

Use Gunicorn (or similar) to serve Django, possibly behind nginx. Example:

pip install gunicorn


Test with:

gunicorn EnergyDetector.wsgi:application --bind 0.0.0.0:8000


Then configure nginx reverse proxy:

server {
    listen 80;
    server_name my.domain.com;  # or EC2 public IP if no domain

    location /static/ {
        alias /home/ubuntu/EnergyDetector/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}


Set up systemd for gunicorn service similarly.

10. Permissions, paths, static files

Collect static files if project uses that: python manage.py collectstatic

Ensure file permissions allow the web server to read them.

Ensure that the energyplus executable is executable by the user running Celery / Django.

11. Starting / enabling services

Enable & start:

sudo systemctl daemon-reload
sudo systemctl enable energydetector-celery.service
sudo systemctl start energydetector-celery.service

sudo systemctl enable gunicorn.service
sudo systemctl start gunicorn.service


Nginx:

sudo apt install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx

12. Testing

Browse to your EC2 public IP or domain to make sure Django is accessible.

Submit a form to trigger EnergyPlus simulation, watch Celery worker logs to ensure the task runs.

Check that outputs are generated as expected.

Possible gotchas

EnergyPlus Dependencies on Linux: sometimes missing shared libs; the installer might expect certain GUI libs even if not needed.

Performance: simulations can be resource heavy; you may need more CPU / RAM.

Security: opening ports, securing the server.

Long-running tasks: Celery timeout, memory leaks.
