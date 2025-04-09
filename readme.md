**Steps Required for setup this project**
Unzip this project 
**1. Install the Energyplus follow these steps:**
1. Visit the official EnergyPlus page:

Choose the Windows installer for the latest version.

2. Run the Installer
Once downloaded, double-click the .exe file.

Follow the installer instructions:

Choose installation directory (default is usually fine)

Accept license agreement

Complete the installation

3. Verify Installation
Open Command Prompt (cmd)

Type:

bash
Copy
Edit
energyplus --version
If installed correctly, it will display the version number.

🔧 Optional: Add EnergyPlus to System PATH
If the energyplus command doesn't work in the terminal:

Find where EnergyPlus was installed (e.g., C:\EnergyPlusV9-6-0)

Copy the path to the bin folder inside it (e.g., C:\EnergyPlusV9-6-0\bin)

Add it to the System PATH:

Open Start Menu → search "Environment Variables"

Click "Edit the system environment variables"

Click "Environment Variables"

Under System variables, find and edit Path

Click New and paste the path

Click OK to apply


**2. open the terminal run the command to install requirements.txt**
activate the virtual environment 
1. python -m venv myenv 
2. .\myenv\Scripts\activate
3. pip install -r requirements.txt

**3. open two terminal in one terminal run this command**
1. python manage.py qcluster
on another terminal run below command 
2. python manage.py runserver
3. open the url fill the form and press simulate button to do some simulations
