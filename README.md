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

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Configure EnergyPlus path
Default expected location:
C:\EnergyPlusV8-9-0\energyplus.exe

If EnergyPlus is installed elsewhere, update:
Calculator/tasks.py
Replace:
ENERGYPLUS_PATH = "C:\\EnergyPlusV8-9-0\\energyplus.exe"
with your installed path.

5️⃣ Run database migrations
python manage.py migrate

6️⃣ Start the Django server
python manage.py runserver

🚀 Usage
Open the browser and navigate to:
http://127.0.0.1:8000
Fill in the form with home parameters.
Submit to see your simulated energy usage.

🛠 Development Notes
The EnergyPlus executable must be correctly set for simulations to work.
Compatible only with EnergyPlus v8.9.0 unless adjusted in code.
