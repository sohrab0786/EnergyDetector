from __future__ import absolute_import, unicode_literals
from celery import shared_task
from threading import Thread
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from Calculator.models import Simple
from pathlib import Path
from Calculator.models import Detailed_Data
from Calculator.models import Parametric_Data
import uuid
import time
from datetime import datetime
import math
import os, errno, sys
import shlex, subprocess
from django.conf import settings
from importlib import import_module
from django.conf import settings
from string import Template
from bs4 import BeautifulSoup,Comment
import requests
import csv
import json
from django.core.mail import send_mail , EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
#from exceptions import Exception
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Thes task is shared to view.py
#@shared_task
def run_simulation_simple(pk):
        # Or handle gracefully
    form_detailed_data = Simple.objects.filter(pk=pk).first()  # Returns None if not found
    if not form_detailed_data:
        print(f"No record found for pk={pk}")
        return  # Prevent further execution
    try:
        file_uuid = form_detailed_data.file_uuid
        Location = form_detailed_data.Location
    except AttributeError:
        print("Missing attributes in form_detailed_data")
        return
    weather_file = os.path.join(BASE_DIR,"static/WeatherData/")+Location+".epw"
    weather_file = str(Path(weather_file))
    print(f'weather file: {weather_file}')
    static_dir = settings.STATICFILES_DIRS[0]
    base_path = os.path.join(static_dir,"model_idf",file_uuid,"base","model.idf")
    base_path = str(Path(base_path))
    print(f'base_path: {base_path}')
    proposed_path = os.path.join(static_dir,"model_idf",file_uuid,"proposed","model.idf")
    proposed_path = str(Path(proposed_path))
    print(f'base_path: {base_path}, proposed_path: {proposed_path}')
    print('running base')
    template_folder_path_base = os.path.join(BASE_DIR,"templates","html_dir",file_uuid,"base")
    template_folder_path_base = str(Path(template_folder_path_base))
    print(f'template_folder_path_base: {template_folder_path_base}')
    ENERGYPLUS_PATH = "C:\\EnergyPlusV8-9-0\\energyplus.exe"
    command_line_base = [ENERGYPLUS_PATH,"-w", weather_file ,"-d",  template_folder_path_base ,"-p" , Location + "base" ,base_path]
    print("command_line after")
    print(command_line_base)
    # Running energy plus
    base_process = subprocess.Popen(command_line_base)
    # Wait till process ends
    base_process.wait()
    base_process_pid = base_process.pid
    print(base_process_pid)
    print('completed running base')
    template_folder_path_proposed = os.path.join(BASE_DIR,"templates","html_dir",file_uuid,"proposed")
    template_folder_path_proposed = str(Path(template_folder_path_proposed)) 
    #ENERGYPLUS_PATH = r"C:/EnergyPlusV8-9-0/energyplus.exe"
    command_line_proposed = [ENERGYPLUS_PATH,"-w", weather_file ,"-d",  template_folder_path_proposed ,"-p" , Location + "proposed"  ,proposed_path]
    print(command_line_proposed)
    proposed_process = subprocess.Popen(command_line_proposed)
    proposed_process_pid =  proposed_process.pid
    print(proposed_process_pid)
    print('completed proposed proposed case')
    proposed_process.wait()
    #base output processing
    html_location_table = Location + "basetbl.htm"
    html_file_base = os.path.join(template_folder_path_base,html_location_table)
    html_file_base = str(Path(html_file_base))
    print(f'base htm created: {html_file_base}')
    try:
        print(f'file path {html_file_base}')
        print(f"File Exists: {os.path.exists(html_file_base)}")  # Check if file exists
        print(f"Is File: {os.path.isfile(html_file_base)}")
        with open(html_file_base, "r", encoding="utf-8") as file:
          page = file.read()
 
    except FileNotFoundError:
        form_detailed_data.delete()
        print("File not found. Check the path.")
        return HttpResponse('Error in IDF File. Contact SysAdmin 1')
    except PermissionError:
        form_detailed_data.delete()
        print("Permission denied. Try running as Admin.")
        return HttpResponse('Error in IDF File. Contact SysAdmin 1')
    except Exception as e:
        form_detailed_data.delete()
        print(f"Unexpected error: {e}")
        return HttpResponse('Error in IDF File. Contact SysAdmin 1')
    soup = BeautifulSoup(page, 'html.parser')
    #print('soup:base htm object',soup.prettify())
    data = []
    base_csv_file = os.path.join(BASE_DIR,"templates","html_dir",file_uuid,"base.csv")
    base_csv_file = str(Path(base_csv_file))    
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        if comment.strip() == "FullName:Annual Building Utility Performance Summary_Entire Facility_End Uses":
            next_node = comment.find_next_sibling("table")  # Find the table directly
            if next_node:
                data.append(next_node)
            break  # Stop after finding the first relevant table
    if not data:
        print("Table not found.")
        exit()
    end = data[0]
    # Extract table rows
    rows = []
    for row in end.find_all("tr"):
        cols = [td.text.strip() for td in row.find_all("td")]
        if cols:  # Skip empty rows
            rows.append(cols)
    # Save to CSV
    base_csv_file = os.path.join(BASE_DIR,"templates","html_dir",file_uuid,"base.csv")
    with open(base_csv_file, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerows(rows)
    print(f"File Exists: {os.path.exists(base_csv_file)}")
    print(f"File Size: {os.path.getsize(base_csv_file)} bytes") 
    # Read CSV and process
    x = []
    with open(base_csv_file, "r", encoding="utf-8") as f:
        data = csv.reader(f)
        for row in data:
            if row:  # Skip empty rows
                x.append(row)
    print(f"Total valid rows collected: {len(x)}")
    # Ensure proper indexing
    header = x[0]
    values = x[1:]
    output = {};
    try:
        output["Heating_Base"] = float(values[0][1]) if values[0][1] else 0.0
        output["Cooling_Base"] = float(values[1][1]) if values[1][1] else 0.0
        output["Interior_Lighting_Base"] = float(values[2][1]) if values[2][1] else 0.0
        output["Interior_Equipment_Base"] = float(values[4][1]) if values[4][1] else 0.0
        output["Fans_Base"] = float(values[6][1]) if values[6][1] else 0.0
        output["Pumps_Base"] = float(values[7][1]) if values[7][1] else 0.0
        output["Heat_Rejection_Base"] = float(values[8][1]) if values[8][1] else 0.0
        output["Total_Base"] = sum(output.values())  # Sum up values dynamically
    except IndexError as e:
        print("Error in data extraction:", e)
    print("Extracted JSON Output:", output)
    output['basecase'] = form_detailed_data.Normal_Roof
    output['proposedcase'] = form_detailed_data.Cool_roof
    print(f'output basecase and proposed case {output["basecase"]}, {output["basecase"]}')
    print('filled! json')
    basecasee = "0.87"
    proposedcasee = "0.87"
    if (output['basecase'] == "0.23"):
        basecasee = "0.87"
    elif (output['basecase'] == "0.22"):
        basecasee = "0.91"
    elif (output['basecase'] == "0.25"):
        basecasee = "0.90"
    elif (output['basecase'] == "0.33"):
        basecasee = "0.90"
    elif (output['basecase'] == "0.34"):
        basecasee = "0.90"
    elif (output['basecase'] == "0.61"):
        basecasee = "0.25"
    elif (output['basecase'] == "0.65"):
        basecasee = "0.90"
    elif (output['basecase'] == "0.67"):
        basecasee = "0.85"
    elif (output['basecase'] == "0.69"):
        basecasee = "0.87"
    elif (output['basecase'] == "0.73"):
        basecasee = "0.90"
    elif (output['basecase'] == "0.80"):
        basecasee = "0.91"
    elif (output['basecase'] == "0.83"):
        basecasee = "0.92"
    elif (output['basecase'] == "0.85"):
        basecasee = "0.91"
    if (output["proposedcase"] == "0.23"):
            proposedcasee = "0.87"
    elif (output["proposedcase"] == "0.22"):
        proposedcasee = "0.91"
    elif (output["proposedcase"] == "0.25"):
        proposedcasee = "0.90"
    elif (output["proposedcase"] == "0.33"):
        proposedcasee = "0.90"
    elif (output["proposedcase"] == "0.34"):
        proposedcasee = "0.90"
    elif (output["proposedcase"] == "0.61"):
        proposedcasee = "0.25"
    elif (output["proposedcase"] == "0.65"):
        proposedcasee = "0.90"
    elif (output["proposedcase"] == "0.67"):
        proposedcasee = "0.85"
    elif (output["proposedcase"] == "0.69"):
        proposedcasee = "0.87"
    elif (output["proposedcase"] == "0.73"):
        proposedcasee = "0.90"
    elif (output["proposedcase"] == "0.80"):
        proposedcasee = "0.91"
    elif (output["proposedcase"] == "0.83"):
        proposedcasee = "0.92"
    elif (output["proposedcase"] == "0.85"):
        proposedcasee = "0.91"        
    output['basecasee'] = basecasee
    output['proposedcasee'] = proposedcasee
    #processing proposed output
    html_location_table = Location + "proposedtbl.htm"
    html_file_proposed = os.path.join(template_folder_path_proposed,html_location_table)
    html_file_proposed = str(Path(html_file_proposed))
    print(f'proposed htm file created: {html_file_proposed}')
    #p1= subprocess.Popen(args1)
    #print(p1)
    with open(html_file_proposed, "r", encoding="utf-8") as file:
       page = file.read()
    #print(page)
    soup = BeautifulSoup(page, 'html.parser')
    #print('soup: object',soup.prettify())
    data = []
    proposed_csv_file = os.path.join(BASE_DIR,"templates","html_dir",file_uuid,"proposed.csv")
    proposed_csv_file = str(Path(proposed_csv_file))
    print(f'proposed csv file created: {proposed_csv_file}')
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        if comment.strip() == "FullName:Annual Building Utility Performance Summary_Entire Facility_End Uses":
            next_node = comment.find_next_sibling("table")  # Find the table directly
            if next_node:
                data.append(next_node)
            break  # Stop after finding the first relevant table
    #if not data:
    #    print("Proposed table not found.")
    #    exit()
    end = data[0]
    # Extract table rows
    rows = []
    for row in end.find_all("tr"):
        cols = [td.text.strip() for td in row.find_all("td")]
        if cols:  # Skip empty rows
            rows.append(cols)
    # Save to CSV
    #proposed_csv_file = "proposed_output.csv"
    with open(proposed_csv_file, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerows(rows)
    print(f"File Exists: {os.path.exists(proposed_csv_file)}")
    print(f"File Size: {os.path.getsize(proposed_csv_file)} bytes") 
    # Read CSV and process
    x = []
    with open(proposed_csv_file, "r", encoding="utf-8") as f:
        data = csv.reader(f)
        for row in data:
            if row:  # Skip empty rows
                x.append(row)
    print(f"Total valid rows collected (proposed): {len(x)}")
    # Ensure proper indexing
    header = x[0]
    values = x[1:]
    try:
        print('start for proposedcase value filling in output')
        output["Heating_Proposed"] = float(values[0][1]) if values[0][1] else 0.0
        print('heating proposed filled!')
        output["Cooling_Proposed"] = float(values[1][1]) if values[1][1] else 0.0
        output["Interior_Lighting_Proposed"] = float(values[2][1]) if values[2][1] else 0.0
        output["Interior_Equipment_Proposed"] = float(values[4][1]) if values[4][1] else 0.0
        output["Fans_Proposed"] = float(values[6][1]) if values[6][1] else 0.0
        output["Pumps_Proposed"] = float(values[7][1]) if values[7][1] else 0.0
        output["Heat_Rejection_Proposed"] = float(values[8][1]) if values[8][1] else 0.0
        output['Total_Proposed'] = float(x[1][1]) + float(x[2][1]) + float(x[3][1]) + float(x[5][1]) + float(x[7][1]) + float(x[8][1]) + float(x[9][1])   # Sum up values dynamically
    except IndexError as e:
        print("Error in data extraction:", e)
    print("Extracted JSON Output (Proposed):", output)
    if "Heating_Base" in output:
       print('heating base in output!')
    if(float(output['Heating_Base']) == 0):
        output['Heating_Savings'] = "0"
    else:
        output['Heating_Savings'] = round((float(output['Heating_Base']) - float(output['Heating_Proposed']))/float(output['Heating_Base'])*100,2)
    if(float(output['Cooling_Base']) == 0):
        output['Cooling_Savings'] = "0"
    else:
        output['Cooling_Savings'] = round((float(output['Cooling_Base']) - float(output['Cooling_Proposed']))/float(output['Cooling_Base'])*100,2)                
    if(float(output['Interior_Lighting_Base']) == 0):
        output['Interior_Lighting_Savings'] = "0"
    else:
        output['Interior_Lighting_Savings'] = round((float(output['Interior_Lighting_Base']) - float(output['Interior_Lighting_Proposed']))/float(output['Interior_Lighting_Base'])*100,2)
    if(float(output['Interior_Equipment_Base']) == 0):
        output['Interior_Equipment_Savings'] = "0"
    else:
        output['Interior_Equipment_Savings'] = round((float(output['Interior_Equipment_Base']) - float(output['Interior_Equipment_Proposed']))/float(output['Interior_Equipment_Base'])*100,2)
    if (float(output['Pumps_Base']) == 0):
        output['Pumps_Savings'] = "0"
    else:
        output['Pumps_Savings'] = round((float(output['Pumps_Base']) - float(output['Pumps_Proposed']))/float(output['Pumps_Base'])*100,2)            
    if (float(output['Heat_Rejection_Base']) == 0):
        output['Heat_Rejection_Savings'] = "0"
    else:
        output['Heat_Rejection_Savings'] = round((float(output['Heat_Rejection_Base']) - float(output['Heat_Rejection_Proposed']))/float(output['Heat_Rejection_Base'])*100,2)
    if (float(output['Fans_Base']) == 0):
        output['Fans_Savings'] = "0"
    else:
        output['Fans_Savings'] = round((float(output['Fans_Base']) - float(output['Fans_Proposed']))/float(output['Fans_Base'])*100,2)
    if (float(output['Total_Base']) == 0):
        output['Total_Base'] = "0"
    else:
        output['Total_Savings'] = round((float(output['Total_Base']) - float(output['Total_Proposed'])),2)
    if (float(output['Total_Base']) == 0):
        output['Total_Savings_Percent'] = "0"
    else:
        output['Total_Savings_Percent'] = round((float(output['Total_Base']) - float(output['Total_Proposed']))/float(output['Total_Base'])*100,2)
    Roof_area = float(form_detailed_data.Roof_area)
    Electricity = form_detailed_data.Electricity
    output['Electricity'] = float(Electricity)
    output['heat_save'] = round((float(output['Heating_Base']) - float(output['Heating_Proposed'])),2)
    output['cool_save'] = round((float(output['Cooling_Base']) - float(output['Cooling_Proposed'])),2)
    output['total_save'] = output['heat_save'] + output['cool_save']
    output['heat_save_area'] = round((float(output['Heating_Base']) - float(output['Heating_Proposed']))/float(Roof_area),2)
    output['cool_save_area'] = round((float(output['Cooling_Base']) - float(output['Cooling_Proposed']))/float(Roof_area),2)
    output['total_save_area'] = output['heat_save_area'] + output['cool_save_area']
    output['heat_save_cost'] = round((float(output['heat_save'])*float(output['Electricity'])),2)
    output['cool_save_cost'] = round((float(output['cool_save'])*float(output['Electricity'])),2)
    output['total_save_cost'] = output['heat_save_cost'] + output['cool_save_cost']
    output['Annual_Savings'] = output['Total_Savings'] * output['Electricity']
    print(output)
    file = open(html_file_base, "r") 
    page = file.read()
    file.close()
    soup = BeautifulSoup(page, 'html.parser')
    data = []
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        if comment.strip() == "FullName:EndUseEnergyConsumptionElectricityMonthly_Meter_Custom Monthly Report":
            next_node = comment.find_next_sibling("table")  # Find the table directly
            if next_node:
                data.append(next_node)
            break  # Stop after finding the first relevant table
    if not data:
        print("Electricity Monthly Report table not found.")
        exit()
    end = data[0]
    # Extract table rows
    rows = []
    for row in end.find_all("tr"):
        cols = [td.text.strip() for td in row.find_all("td")]
        if cols:  # Skip empty rows
            rows.append(cols)
    # Save to CSV
    output_csv_file = "out.csv"
    with open(output_csv_file, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerows(rows)
    print(f"File Exists: {os.path.exists(output_csv_file)}")
    print(f"File Size: {os.path.getsize(output_csv_file)} bytes")  
    # Read CSV and process
    x = []
    with open(output_csv_file, "r", encoding="utf-8") as f:
        data = csv.reader(f)
        for row in data:
            if row:  # Skip empty rows
                x.append(row)
    print(f"Total valid rows collected: {len(x)}")
    # Define months
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    # Extract heating and cooling values safely
    heating_base = []
    cooling_base = []
    for i in range(1,13):
        heating_base.append(float(x[i][7]))
        cooling_base.append(float(x[i][8]))
    # Create the final list of tuples
    mylist_base = list(zip(months, heating_base, cooling_base))
    # Store in output dictionary
    output['mylist_base'] = mylist_base
    print("Extracted JSON Output:", output)
    file = open(html_file_proposed, "r") 
    page = file.read()
    file.close()
    soup = BeautifulSoup(page, 'html.parser')
    data = []
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        if comment.strip() == "FullName:EndUseEnergyConsumptionElectricityMonthly_Meter_Custom Monthly Report":
            next_node = comment.find_next_sibling("table")  # Find the table directly
            if next_node:
                data.append(next_node)
            break  # Stop after finding the first relevant table
    if not data:
        print("Electricity Monthly Report table not found.")
        exit()
    end = data[0]
    # Extract table rows
    rows = []
    for row in end.find_all("tr"):
        cols = [td.text.strip() for td in row.find_all("td")]
        if cols:  # Skip empty rows
            rows.append(cols)
    # Save to CSV
    output_csv_file = "out.csv"
    with open(output_csv_file, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerows(rows)
    print(f"File Exists: {os.path.exists(output_csv_file)}")
    print(f"File Size: {os.path.getsize(output_csv_file)} bytes")  
    # Read CSV and process
    x = []
    with open(output_csv_file, "r", encoding="utf-8") as f:
        data = csv.reader(f)
        for row in data:
            if row:  # Skip empty rows
                x.append(row)
    print(f"Total valid rows collected: {len(x)}")
    # Define months
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    # Extract heating and cooling values safely
    heating_proposed = []
    cooling_proposed = []
    for i in range(1,13):
        heating_proposed.append(float(x[i][7]))
        cooling_proposed.append(float(x[i][8]))
    mylist_proposed = zip(months, heating_proposed,cooling_proposed)
    heating_compare = zip(months,heating_base,heating_proposed)
    cooling_compare = zip(months,cooling_base,cooling_proposed)
    heating_compare = [[key,value1,value2] for key,value1,value2 in heating_compare]
    cooling_compare = [[key,value1,value2] for key,value1,value2 in cooling_compare]
    output['mylist_proposed'] = mylist_proposed
    output['heating_compare'] = heating_compare
    output['cooling_compare'] = cooling_compare
    print("Extracted JSON Output:", output)
    print('done processing results') 
    print("Available keys in output:", list(output.keys()))
    db_list = ['cooling_compare','heating_compare','Total_Savings','Annual_Savings','Heating_Base','Heating_Proposed','Heating_Savings','Cooling_Base','Cooling_Proposed','Cooling_Savings','Interior_Equipment_Base','Interior_Equipment_Proposed','Interior_Equipment_Savings',"Interior_Lighting_Base","Interior_Lighting_Proposed",
        "Interior_Lighting_Savings",'Fans_Base','Fans_Proposed','Fans_Savings',
        "Pumps_Base","Pumps_Proposed","Pumps_Savings","Heat_Rejection_Base",
        "Heat_Rejection_Proposed","Heat_Rejection_Savings","Total_Base","Total_Proposed","Total_Savings_Percent","heat_save","cool_save","total_save",
        "heat_save_area","cool_save_area","total_save_acrea","heat_save_cost","cool_save_cost","total_save_cost"]    
    for value in db_list:
      if value in output:
        setattr(form_detailed_data, value, output[value])
      else:
        print(f"Warning: '{value}' not found in output.") 
    print('set attr done!')
    form_detailed_data.heating_compare = json.dumps(heating_compare)
    form_detailed_data.cooling_compare = json.dumps(cooling_compare)
    form_detailed_data.save()
    emailid = form_detailed_data.emailid
    print('data saved')
    if emailid:
        subject = 'Cool Roof Calculator results'
        message = 'http://localhost:8000/display_results/' + str(pk) + "/"
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [emailid]

        print("\n======== Email Sending Debug ========")
        print(f"Subject: {subject}")
        print(f"Message: {message}")
        print(f"Email From: {email_from}")
        print(f"Recipient List: {recipient_list}")
        
        try:
            result = send_mail(subject, message, email_from, recipient_list, fail_silently=False)
            print(f"send_mail result: {result}")  # Should be 1 if successful
            if result == 1:
                print("✅ Email sent successfully!")
            else:
                print("❌ Email failed to send (return value 0).")
        except Exception as e:
            print("❌ Email sending failed:", e)
        

#@shared_task
def run_simulation(pk):
    
    try:
        form_detailed_data = Detailed_Data.objects.get(pk = pk)
    except Detailed_Data.DoesNotExist:
        raise Exception('invalid pk')

    file_uuid = form_detailed_data.file_uuid
    Location = form_detailed_data.Location
    weather_file = str(Path(os.path.join(BASE_DIR,"static/WeatherData/")+Location+".epw"))
    static_dir = settings.STATICFILES_DIRS[0]
    base_path = str(Path(os.path.join(static_dir,"model_idf",file_uuid,"base","model.idf")))
    proposed_path = str(Path(os.path.join(static_dir,"model_idf",file_uuid,"proposed","model.idf")))

    print('running base')

    template_folder_path_base = str(Path(os.path.join(BASE_DIR,"templates","html_dir",file_uuid,"base")))
    ENERGYPLUS_PATH = "C:\\EnergyPlusV8-9-0\\energyplus.exe"
    command_line_base = [ENERGYPLUS_PATH,"-w", weather_file ,"-d",  template_folder_path_base ,"-p" , Location + "base" ,base_path]
    print("command_line after")
    print(command_line_base)
    base_process = subprocess.Popen(command_line_base)
    base_process.wait()
    base_process_pid = base_process.pid
    print(base_process_pid)
    print('completed running base')

    template_folder_path_proposed = str(Path(os.path.join(BASE_DIR,"templates","html_dir",file_uuid,"proposed"))) 

    print('running proposed')
    #ENERGYPLUS_PATH = "C:\\EnergyPlusV8-9-0\\energyplus.exe"
    command_line_proposed = [ENERGYPLUS_PATH,"-w", weather_file ,"-d",  template_folder_path_proposed ,"-p" , Location + "proposed"  ,proposed_path]
    print(command_line_proposed)
    proposed_process = subprocess.Popen(command_line_proposed)
 
    proposed_process_pid =  proposed_process.pid
    print(proposed_process_pid)
    proposed_process.wait()
    print('completed proposed')

    #base output processing
    html_location_table = Location + "basetbl.htm"
    html_file_base = os.path.join(template_folder_path_base,html_location_table)
    html_file_base = str(Path(html_file_base))
    print(html_file_base)


    try:
        print(f'file path {html_file_base}')
        print(f"File Exists: {os.path.exists(html_file_base)}")  # Check if file exists
        print(f"Is File: {os.path.isfile(html_file_base)}")
        with open(html_file_base, "r", encoding="utf-8") as file:
           page = file.read()
    except FileNotFoundError:
        form_detailed_data.delete()
        print("File not found. Check the path.")
        return HttpResponse('Error in IDF File. Contact SysAdmin 1')
    except PermissionError:
        form_detailed_data.delete()
        print("Permission denied. Try running as Admin.")
        return HttpResponse('Error in IDF File. Contact SysAdmin 1')
    except Exception as e:
        form_detailed_data.delete()
        print(f"Unexpected error: {e}")
        return HttpResponse('Error in IDF File. Contact SysAdmin 1')

    soup = BeautifulSoup(page, 'html.parser')

    data = []

    #base_csv_file = os.path.join(BASE_DIR,"templates","html_dir",file_uuid,"base.csv")
    base_csv_file = str(Path(os.path.join(BASE_DIR,"templates","html_dir",file_uuid,"base.csv")))
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        if comment.strip() == "FullName:Annual Building Utility Performance Summary_Entire Facility_End Uses":
            next_node = comment.find_next_sibling("table")  # Find the table directly
            if next_node:
                data.append(next_node)
            break  # Stop after finding the first relevant table
    if not data:
        print("Table not found.")
        exit()
    end = data[0]
    # Extract table rows
    rows = []
    for row in end.find_all("tr"):
        cols = [td.text.strip() for td in row.find_all("td")]
        if cols:  # Skip empty rows
            rows.append(cols)
    # Save to CSV
    
    with open(base_csv_file, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerows(rows)
    print(f"File Exists: {os.path.exists(base_csv_file)}")
    print(f"File Size: {os.path.getsize(base_csv_file)} bytes") 
    # Read CSV and process
    x = []
    with open(base_csv_file, "r", encoding="utf-8") as f:
        data = csv.reader(f)
        for row in data:
            if row:  # Skip empty rows
                x.append(row)
    print(f"Total valid rows collected: {len(x)}")
    # Ensure proper indexing
    header = x[0]
    values = x[1:]
    output = {};
    try:
        output["Heating_Base"] = float(values[0][1]) if values[0][1] else 0.0
        output["Cooling_Base"] = float(values[1][1]) if values[1][1] else 0.0
        output["Interior_Lighting_Base"] = float(values[2][1]) if values[2][1] else 0.0
        output["Interior_Equipment_Base"] = float(values[4][1]) if values[4][1] else 0.0
        output["Fans_Base"] = float(values[6][1]) if values[6][1] else 0.0
        output["Pumps_Base"] = float(values[7][1]) if values[7][1] else 0.0
        output["Heat_Rejection_Base"] = float(values[8][1]) if values[8][1] else 0.0
        output["Total_Base"] = sum(output.values())  # Sum up values dynamically
    except IndexError as e:
        print("Error in data extraction:", e)
    print("Extracted JSON Output:", output)
    Reflectivity_base = form_detailed_data.Reflectivity_base
    Emissivity_base = form_detailed_data.Emissivity_base
    output['basecase'] = Reflectivity_base
    output['basecasee'] = Emissivity_base

    #processing proposed output

    html_location_table = Location + "proposedtbl.htm"
    html_file_proposed = str(Path(os.path.join(template_folder_path_proposed,html_location_table)))
    print(html_file_proposed)


    with open(html_file_proposed, "r", encoding="utf-8") as file:
       page = file.read()

    soup = BeautifulSoup(page, 'html.parser')

    data = []

    #proposed_csv_file = os.path.join(BASE_DIR,"templates","html_dir",file_uuid,"proposed.csv")
    proposed_csv_file = str(Path(os.path.join(BASE_DIR,"templates","html_dir",file_uuid,"proposed.csv")))

    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        if comment.strip() == "FullName:Annual Building Utility Performance Summary_Entire Facility_End Uses":
            next_node = comment.find_next_sibling("table")  # Find the table directly
            if next_node:
                data.append(next_node)
            break  # Stop after finding the first relevant table
    #if not data:
    #    print("Proposed table not found.")
    #    exit()
    end = data[0]
    # Extract table rows
    rows = []
    for row in end.find_all("tr"):
        cols = [td.text.strip() for td in row.find_all("td")]
        if cols:  # Skip empty rows
            rows.append(cols)
    # Save to CSV
    with open(proposed_csv_file, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerows(rows)
    print(f"File Exists: {os.path.exists(proposed_csv_file)}")
    print(f"File Size: {os.path.getsize(proposed_csv_file)} bytes") 
    # Read CSV and process
    x = []
    with open(proposed_csv_file, "r", encoding="utf-8") as f:
        data = csv.reader(f)
        for row in data:
            if row:  # Skip empty rows
                x.append(row)
    print(f"Total valid rows collected (proposed): {len(x)}")
    # Ensure proper indexing
    header = x[0]
    values = x[1:]
    try:
        print('start for proposedcase value filling in output')
        output["Heating_Proposed"] = float(values[0][1]) if values[0][1] else 0.0
        print('heating proposed filled!')
        output["Cooling_Proposed"] = float(values[1][1]) if values[1][1] else 0.0
        output["Interior_Lighting_Proposed"] = float(values[2][1]) if values[2][1] else 0.0
        output["Interior_Equipment_Proposed"] = float(values[4][1]) if values[4][1] else 0.0
        output["Fans_Proposed"] = float(values[6][1]) if values[6][1] else 0.0
        output["Pumps_Proposed"] = float(values[7][1]) if values[7][1] else 0.0
        output["Heat_Rejection_Proposed"] = float(values[8][1]) if values[8][1] else 0.0
        output['Total_Proposed'] = float(x[1][1]) + float(x[2][1]) + float(x[3][1]) + float(x[5][1]) + float(x[7][1]) + float(x[8][1]) + float(x[9][1])   # Sum up values dynamically
    except IndexError as e:
        print("Error in data extraction:", e)
    print("Extracted JSON Output (Proposed):", output)
    
    Reflectivity_proposed = form_detailed_data.Reflectivity_proposed
    Emissivity_proposed = form_detailed_data.Emissivity_proposed
    output['proposedcase'] = Reflectivity_proposed
    output['proposedcasee'] = Emissivity_proposed
    if(float(output['Heating_Base']) == 0):
        output['Heating_Savings'] = "0"
    else:
        output['Heating_Savings'] = round((float(output['Heating_Base']) - float(output['Heating_Proposed']))/float(output['Heating_Base'])*100,2)

    if(float(output['Cooling_Base']) == 0):
        output['Cooling_Savings'] = "0"
    else:
        output['Cooling_Savings'] = round((float(output['Cooling_Base']) - float(output['Cooling_Proposed']))/float(output['Cooling_Base'])*100,2)                

    if(float(output['Interior_Lighting_Base']) == 0):
        output['Interior_Lighting_Savings'] = "0"
    else:
        output['Interior_Lighting_Savings'] = round((float(output['Interior_Lighting_Base']) - float(output['Interior_Lighting_Proposed']))/float(output['Interior_Lighting_Base'])*100,2)

    if(float(output['Interior_Equipment_Base']) == 0):
        output['Interior_Equipment_Savings'] = "0"
    else:
        output['Interior_Equipment_Savings'] = round((float(output['Interior_Equipment_Base']) - float(output['Interior_Equipment_Proposed']))/float(output['Interior_Equipment_Base'])*100,2)


    if (float(output['Pumps_Base']) == 0):
        output['Pumps_Savings'] = "0"
    else:
        output['Pumps_Savings'] = round((float(output['Pumps_Base']) - float(output['Pumps_Proposed']))/float(output['Pumps_Base'])*100,2)
            
    if (float(output['Heat_Rejection_Base']) == 0):
        output['Heat_Rejection_Savings'] = "0"
    else:
        output['Heat_Rejection_Savings'] = round((float(output['Heat_Rejection_Base']) - float(output['Heat_Rejection_Proposed']))/float(output['Heat_Rejection_Base'])*100,2)

    if (float(output['Fans_Base']) == 0):
        output['Fans_Savings'] = "0"
    else:
        output['Fans_Savings'] = round((float(output['Fans_Base']) - float(output['Fans_Proposed']))/float(output['Fans_Base'])*100,2)

    if (float(output['Total_Base']) == 0):
        output['Total_Base'] = "0"
    else:
        output['Total_Savings'] = round((float(output['Total_Base']) - float(output['Total_Proposed'])),2)

    if (float(output['Total_Base']) == 0):
        output['Total_Savings_Percent'] = "0"
    else:
        output['Total_Savings_Percent'] = round((float(output['Total_Base']) - float(output['Total_Proposed']))/float(output['Total_Base'])*100,2)
            
    print('done el if condition, for output')
    
    Roof_area = float(form_detailed_data.Roof_area)
    Electricity = form_detailed_data.Electricity
    output['Electricity'] = float(Electricity)

    output['heat_save'] = round((float(output['Heating_Base']) - float(output['Heating_Proposed'])),2)
    output['cool_save'] = round((float(output['Cooling_Base']) - float(output['Cooling_Proposed'])),2)
    output['total_save'] = output['heat_save'] + output['cool_save']

    output['heat_save_area'] = round((float(output['Heating_Base']) - float(output['Heating_Proposed']))/float(Roof_area),2)
    output['cool_save_area'] = round((float(output['Cooling_Base']) - float(output['Cooling_Proposed']))/float(Roof_area),2)
    output['total_save_area'] = output['heat_save_area'] + output['cool_save_area']
    
    
    output['heat_save_cost'] = round((float(output['heat_save'])*float(output['Electricity'])),2)
    output['cool_save_cost'] = round((float(output['cool_save'])*float(output['Electricity'])),2)
    output['total_save_cost'] = output['heat_save_cost'] + output['cool_save_cost']
    
    output['Annual_Savings'] = output['Total_Savings'] * output['Electricity']
    #print(output)

    print('done output parameter value saving')
    file = open(html_file_base, "r") 
    page = file.read()
    file.close()

    soup = BeautifulSoup(page, 'html.parser')

    data = []

    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        if comment.strip() == "FullName:EndUseEnergyConsumptionElectricityMonthly_Meter_Custom Monthly Report":
            next_node = comment.find_next_sibling("table")  # Find the table directly
            if next_node:
                data.append(next_node)
            break  # Stop after finding the first relevant table
    if not data:
        print("Electricity Monthly Report table not found.")
        exit()
    end = data[0]
    # Extract table rows
    rows = []
    for row in end.find_all("tr"):
        cols = [td.text.strip() for td in row.find_all("td")]
        if cols:  # Skip empty rows
            rows.append(cols)
    template_folder_path_csv =  str(Path(os.path.join(BASE_DIR,"templates","html_dir",file_uuid,"out.csv")))
    with open(template_folder_path_csv, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerows(rows)
        #wr.writerows([[td.text.encode("utf-8") for td in row.find_all("td")] for row in end.select("tr + tr")])
    
    x = []
    with open(template_folder_path_csv,"r", encoding="utf-8") as f:
        data = csv.reader(f)
        for row in data:
            print('row: ',row)
            if row:
              x.append(row)
    print('valid rows len of x : ',len(x))
    months = ['Jan','Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    heating_base = []
    cooling_base = []
    print('starting for loop!')
    for i in range(1,13):
        heating_base.append(float(x[i][7]))
        cooling_base.append(float(x[i][8]))
    print('done for loop')
    mylist_base = zip(months, heating_base,cooling_base) 
    output['mylist_base'] = mylist_base
    file = open(html_file_proposed, "r") 
    page = file.read()
    file.close()
    soup = BeautifulSoup(page, 'html.parser')

    data = []

    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        if comment.strip() == "FullName:EndUseEnergyConsumptionElectricityMonthly_Meter_Custom Monthly Report":
            next_node = comment.find_next_sibling("table")  # Find the table directly
            if next_node:
                data.append(next_node)
            break  # Stop after finding the first relevant table
    if not data:
        print("Electricity Monthly Report table not found.")
        exit()
    end = data[0]
    # Extract table rows
    rows = []
    for row in end.find_all("tr"):
        cols = [td.text.strip() for td in row.find_all("td")]
        if cols:  # Skip empty rows
            rows.append(cols)
    with open(template_folder_path_csv, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerows(rows)
        #wr.writerows([[td.text.encode("utf-8") for td in row.find_all("td")] for row in end.select("tr + tr")])

    x = []
    with open(template_folder_path_csv,"r", encoding="utf-8") as f:
        data = csv.reader(f)
        for row in data:
            x.append(row)

    print(f"Total valid rows collected: {len(x)}")

    months = ['Jan','Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    heating_proposed = []
    cooling_proposed = []
    for i in range(1,13):
        heating_proposed.append(float(x[i][7]))
        cooling_proposed.append(float(x[i][8]))

    mylist_proposed = zip(months, heating_proposed,cooling_proposed)


    heating_compare = zip(months,heating_base,heating_proposed)
    cooling_compare = zip(months,cooling_base,cooling_proposed)
    heating_compare = [[key,value1,value2] for key,value1,value2 in heating_compare]
    cooling_compare = [[key,value1,value2] for key,value1,value2 in cooling_compare]
    output['mylist_proposed'] = mylist_proposed
    output['heating_compare'] = heating_compare
    output['cooling_compare'] = cooling_compare
    print('done processing results')
    db_list = ['cooling_compare','heating_compare','Total_Savings','Annual_Savings','Heating_Base','Heating_Proposed','Heating_Savings','Cooling_Base','Cooling_Proposed','Cooling_Savings','Interior_Equipment_Base','Interior_Equipment_Proposed','Interior_Equipment_Savings',"Interior_Lighting_Base","Interior_Lighting_Proposed",
        "Interior_Lighting_Savings",'Fans_Base','Fans_Proposed','Fans_Savings',
        "Pumps_Base","Pumps_Proposed","Pumps_Savings","Heat_Rejection_Base",
        "Heat_Rejection_Proposed","Heat_Rejection_Savings","Total_Base","Total_Proposed","Total_Savings_Percent","heat_save","cool_save","total_save",
        "heat_save_area","cool_save_area","total_save_area","heat_save_cost","cool_save_cost","total_save_cost"]    
    for value in db_list:
        if value in output:
          setattr(form_detailed_data, value, output[value])
        else:
          print(f"Warning: '{value}' not found in output.") 
   
    form_detailed_data.heating_compare = json.dumps(heating_compare)
    form_detailed_data.cooling_compare = json.dumps(cooling_compare)
    form_detailed_data.save()
    emailid = form_detailed_data.emailid
    
    if emailid:
        subject = 'Cool Roof Calculator results'
        message = 'http://localhost:8000/display_results/' + str(pk) + "/"
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [emailid]

        print("\n======== Email Sending Debug ========")
        print(f"Subject: {subject}")
        print(f"Message: {message}")
        print(f"Email From: {email_from}")
        print(f"Recipient List: {recipient_list}")
        
        try:
            result = send_mail(subject, message, email_from, recipient_list, fail_silently=False)
            print(f"send_mail result: {result}")  # Should be 1 if successful
            if result == 1:
                print("✅ Email sent successfully!")
            else:
                print("❌ Email failed to send (return value 0).")
        except Exception as e:
            print("❌ Email sending failed:", e)

#@shared_task
def run_simulation_parametric(pk):
    
    try:
        form_detailed_data = Parametric_Data.objects.get(pk = pk)
    except Parametric_Data.DoesNotExist:
        raise Exception('invalid pk')

    file_uuid = form_detailed_data.file_uuid
    Location = form_detailed_data.Location
    weather_file = str(Path(os.path.join(BASE_DIR,"static/WeatherData/")+Location+".epw"))
    static_dir = settings.STATICFILES_DIRS[0]
    base_path = str(Path(os.path.join(static_dir,"model_idf",file_uuid,"base","model.idf")))
    proposed_path = str(Path(os.path.join(static_dir,"model_idf",file_uuid,"proposed","model.idf")))

    print('running base')

    template_folder_path_base = str(Path(os.path.join(BASE_DIR,"templates","html_dir",file_uuid,"base")))
    ENERGYPLUS_PATH = "C:\\EnergyPlusV8-9-0\\energyplus.exe"
    command_line_base = [ENERGYPLUS_PATH,"-w", weather_file ,"-d",  template_folder_path_base ,"-p" , Location + "base"  ,base_path]
    print("command_line after")
    print(command_line_base)
    base_process = subprocess.Popen(command_line_base)
    base_process.wait()
    base_process_pid = base_process.pid
    print(base_process_pid)
    print('completed running base')

    template_folder_path_proposed = str(Path(os.path.join(BASE_DIR,"templates","html_dir",file_uuid,"proposed") ))

    print('running proposed')
    #ENERGYPLUS_PATH = r"C:/EnergyPlusV8-9-0/energyplus.exe"
    command_line_proposed = [ENERGYPLUS_PATH,"-w", weather_file ,"-d",  template_folder_path_proposed ,"-p" , Location + "proposed"  ,proposed_path]
    print(command_line_proposed)
    proposed_process = subprocess.Popen(command_line_proposed)
    
    proposed_process_pid =  proposed_process.pid
    print(proposed_process_pid)
    proposed_process.wait()
    print('completed proposed')

    #base output processing
    html_location_table = Location + "basetbl.htm"
    html_file_base = str(Path(os.path.join(template_folder_path_base,html_location_table)))
    print(html_file_base)
    try:
        file = open(html_file_base,"r")
        page = file.read()
        file.close()
    except IOError:
        form_detailed_data.delete()
        return HttpResponse('Error in IDF File. Contact SysAdmin3')

    soup = BeautifulSoup(page, 'html.parser')

    data = []

    base_csv_file = str(Path(os.path.join(BASE_DIR,"templates","html_dir",file_uuid,"base.csv")))

    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        if comment.strip() == "FullName:Annual Building Utility Performance Summary_Entire Facility_End Uses":
            next_node = comment.find_next_sibling("table")  # Find the table directly
            if next_node:
                data.append(next_node)
            break  # Stop after finding the first relevant table
    if not data:
        print("Table not found.")
        exit()
    end = data[0]
    # Extract table rows
    rows = []
    for row in end.find_all("tr"):
        cols = [td.text.strip() for td in row.find_all("td")]
        if cols:  # Skip empty rows
            rows.append(cols)
    # Save to CSV

    with open(base_csv_file, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerows(rows)
    print(f"File Exists: {os.path.exists(base_csv_file)}")
    print(f"File Size: {os.path.getsize(base_csv_file)} bytes") 
    # Read CSV and process
    x = []
    with open(base_csv_file, "r", encoding="utf-8") as f:
        data = csv.reader(f)
        for row in data:
            if row:  # Skip empty rows
                x.append(row)
    print(f"Total valid rows collected: {len(x)}")
    # Ensure proper indexing
    header = x[0]
    values = x[1:]
    output = {};
    try:
        output["Heating_Base"] = float(values[0][1]) if values[0][1] else 0.0
        output["Cooling_Base"] = float(values[1][1]) if values[1][1] else 0.0
        output["Interior_Lighting_Base"] = float(values[2][1]) if values[2][1] else 0.0
        output["Interior_Equipment_Base"] = float(values[4][1]) if values[4][1] else 0.0
        output["Fans_Base"] = float(values[6][1]) if values[6][1] else 0.0
        output["Pumps_Base"] = float(values[7][1]) if values[7][1] else 0.0
        output["Heat_Rejection_Base"] = float(values[8][1]) if values[8][1] else 0.0
        output["Total_Base"] = sum(output.values())  # Sum up values dynamically
    except IndexError as e:
        print("Error in data extraction:", e)
    print("Extracted JSON Output:", output)
    Reflectivity_base = form_detailed_data.Reflectivity_base
    Emissivity_base = form_detailed_data.Emissivity_base
    output['basecase'] = Reflectivity_base
    output['basecasee'] = Emissivity_base

    #processing proposed output

    html_location_table = Location + "proposedtbl.htm"
    html_file_proposed = os.path.join(template_folder_path_proposed,html_location_table)
    print(html_file_proposed)

    
    file = open(html_file_proposed,"r")
    page = file.read()
    file.close()
 
    soup = BeautifulSoup(page, 'html.parser')

    data = []

    proposed_csv_file = os.path.join(BASE_DIR,"templates","html_dir",file_uuid,"proposed.csv")
    
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        if comment.strip() == "FullName:Annual Building Utility Performance Summary_Entire Facility_End Uses":
            next_node = comment.find_next_sibling("table")  # Find the table directly
            if next_node:
                data.append(next_node)
            break  # Stop after finding the first relevant table
    #if not data:
    #    print("Proposed table not found.")
    #    exit()
    end = data[0]
    # Extract table rows
    rows = []
    for row in end.find_all("tr"):
        cols = [td.text.strip() for td in row.find_all("td")]
        if cols:  # Skip empty rows
            rows.append(cols)
    # Save to CSV
 
    with open(proposed_csv_file, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerows(rows)
    print(f"File Exists: {os.path.exists(proposed_csv_file)}")
    print(f"File Size: {os.path.getsize(proposed_csv_file)} bytes") 
    # Read CSV and process
    x = []
    with open(proposed_csv_file, "r", encoding="utf-8") as f:
        data = csv.reader(f)
        for row in data:
            if row:  # Skip empty rows
                x.append(row)
    print(f"Total valid rows collected (proposed): {len(x)}")
    # Ensure proper indexing
    header = x[0]
    values = x[1:]
    try:
        print('start for proposedcase value filling in output')
        output["Heating_Proposed"] = float(values[0][1]) if values[0][1] else 0.0
        print('heating proposed filled!')
        output["Cooling_Proposed"] = float(values[1][1]) if values[1][1] else 0.0
        output["Interior_Lighting_Proposed"] = float(values[2][1]) if values[2][1] else 0.0
        output["Interior_Equipment_Proposed"] = float(values[4][1]) if values[4][1] else 0.0
        output["Fans_Proposed"] = float(values[6][1]) if values[6][1] else 0.0
        output["Pumps_Proposed"] = float(values[7][1]) if values[7][1] else 0.0
        output["Heat_Rejection_Proposed"] = float(values[8][1]) if values[8][1] else 0.0
        output['Total_Proposed'] = float(x[1][1]) + float(x[2][1]) + float(x[3][1]) + float(x[5][1]) + float(x[7][1]) + float(x[8][1]) + float(x[9][1])   # Sum up values dynamically
    except IndexError as e:
        print("Error in data extraction:", e)
    print("Extracted JSON Output (Proposed):", output)
    Reflectivity_proposed = form_detailed_data.Reflectivity_proposed
    Emissivity_proposed = form_detailed_data.Emissivity_proposed
    output['proposedcase'] = Reflectivity_proposed
    output['proposedcasee'] = Emissivity_proposed






    if(float(output['Heating_Base']) == 0):
        output['Heating_Savings'] = "0"
    else:
        output['Heating_Savings'] = round((float(output['Heating_Base']) - float(output['Heating_Proposed']))/float(output['Heating_Base'])*100,2)

    if(float(output['Cooling_Base']) == 0):
        output['Cooling_Savings'] = "0"
    else:
        output['Cooling_Savings'] = round((float(output['Cooling_Base']) - float(output['Cooling_Proposed']))/float(output['Cooling_Base'])*100,2)                

    if(float(output['Interior_Lighting_Base']) == 0):
        output['Interior_Lighting_Savings'] = "0"
    else:
        output['Interior_Lighting_Savings'] = round((float(output['Interior_Lighting_Base']) - float(output['Interior_Lighting_Proposed']))/float(output['Interior_Lighting_Base'])*100,2)

    if(float(output['Interior_Equipment_Base']) == 0):
        output['Interior_Equipment_Savings'] = "0"
    else:
        output['Interior_Equipment_Savings'] = round((float(output['Interior_Equipment_Base']) - float(output['Interior_Equipment_Proposed']))/float(output['Interior_Equipment_Base'])*100,2)


    if (float(output['Pumps_Base']) == 0):
        output['Pumps_Savings'] = "0"
    else:
        output['Pumps_Savings'] = round((float(output['Pumps_Base']) - float(output['Pumps_Proposed']))/float(output['Pumps_Base'])*100,2)
            
    if (float(output['Heat_Rejection_Base']) == 0):
        output['Heat_Rejection_Savings'] = "0"
    else:
        output['Heat_Rejection_Savings'] = round((float(output['Heat_Rejection_Base']) - float(output['Heat_Rejection_Proposed']))/float(output['Heat_Rejection_Base'])*100,2)

    if (float(output['Fans_Base']) == 0):
        output['Fans_Savings'] = "0"
    else:
        output['Fans_Savings'] = round((float(output['Fans_Base']) - float(output['Fans_Proposed']))/float(output['Fans_Base'])*100,2)

    if (float(output['Total_Base']) == 0):
        output['Total_Base'] = "0"
    else:
        output['Total_Savings'] = round((float(output['Total_Base']) - float(output['Total_Proposed'])),2)

    if (float(output['Total_Base']) == 0):
        output['Total_Savings_Percent'] = "0"
    else:
        output['Total_Savings_Percent'] = round((float(output['Total_Base']) - float(output['Total_Proposed']))/float(output['Total_Base'])*100,2)
            


    Roof_area = float(form_detailed_data.Roof_area)
    Electricity = form_detailed_data.Electricity
    output['Electricity'] = float(Electricity)

    output['heat_save'] = round((float(output['Heating_Base']) - float(output['Heating_Proposed'])),2)
    output['cool_save'] = round((float(output['Cooling_Base']) - float(output['Cooling_Proposed'])),2)
    output['total_save'] = output['heat_save'] + output['cool_save']

    output['heat_save_area'] = round((float(output['Heating_Base']) - float(output['Heating_Proposed']))/float(Roof_area),2)
    output['cool_save_area'] = round((float(output['Cooling_Base']) - float(output['Cooling_Proposed']))/float(Roof_area),2)
    output['total_save_area'] = output['heat_save_area'] + output['cool_save_area']
    
    
    output['heat_save_cost'] = round((float(output['heat_save'])*float(output['Electricity'])),2)
    output['cool_save_cost'] = round((float(output['cool_save'])*float(output['Electricity'])),2)
    output['total_save_cost'] = output['heat_save_cost'] + output['cool_save_cost']
    
    output['Annual_Savings'] = output['Total_Savings'] * output['Electricity']
    print(output)


    file = open(html_file_base, "r") 
    page = file.read()
    file.close()

    soup = BeautifulSoup(page, 'html.parser')

    data = []

    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        if comment.strip() == "FullName:EndUseEnergyConsumptionElectricityMonthly_Meter_Custom Monthly Report":
            next_node = comment.find_next_sibling("table")  # Find the table directly
            if next_node:
                data.append(next_node)
            break  # Stop after finding the first relevant table
    if not data:
        print("Electricity Monthly Report table not found.")
        exit()
    end = data[0]
    # Extract table rows
    rows = []
    for row in end.find_all("tr"):
        cols = [td.text.strip() for td in row.find_all("td")]
        if cols:  # Skip empty rows
            rows.append(cols)
    template_folder_path_csv =  str(Path(os.path.join(BASE_DIR,"templates","html_dir",file_uuid,"out.csv")))
    with open(template_folder_path_csv, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerows(rows)
        #wr.writerows([[td.text.encode("utf-8") for td in row.find_all("td")] for row in end.select("tr + tr")])

    x = []
    with open(template_folder_path_csv,"r", encoding="utf-8") as f:
        data = csv.reader(f)
        for row in data:
            #print(row)
            x.append(row)

    print(len(x))

    months = ['Jan','Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    heating_base = []
    cooling_base = []
    for i in range(1,13):
        heating_base.append(float(x[i][7]))
        cooling_base.append(float(x[i][8]))

    mylist_base = zip(months, heating_base,cooling_base)



    # print(mylist_base

    output['mylist_base'] = mylist_base


    file = open(html_file_proposed, "r") 
    page = file.read()
    file.close()

    soup = BeautifulSoup(page, 'html.parser')

    data = []

    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        if comment.strip() == "FullName:EndUseEnergyConsumptionElectricityMonthly_Meter_Custom Monthly Report":
            next_node = comment.find_next_sibling("table")  # Find the table directly
            if next_node:
                data.append(next_node)
            break  # Stop after finding the first relevant table
    if not data:
        print("Electricity Monthly Report table not found.")
        exit()
    end = data[0]
    # Extract table rows
    rows = []
    for row in end.find_all("tr"):
        cols = [td.text.strip() for td in row.find_all("td")]
        if cols:  # Skip empty rows
            rows.append(cols)
    with open(template_folder_path_csv, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerows(rows)
        #wr.writerows([[td.text.encode("utf-8") for td in row.find_all("td")] for row in end.select("tr + tr")])

    x = []
    with open(template_folder_path_csv,"r", encoding="utf-8") as f:
        data = csv.reader(f)
        for row in data:
           
            x.append(row)

    print(len(x))

    months = ['Jan','Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    heating_proposed = []
    cooling_proposed = []
    for i in range(1,13):
        heating_proposed.append(float(x[i][7]))
        cooling_proposed.append(float(x[i][8]))

    mylist_proposed = zip(months, heating_proposed,cooling_proposed)


    heating_compare = zip(months,heating_base,heating_proposed)
    cooling_compare = zip(months,cooling_base,cooling_proposed)
    

    heating_compare = [[key,value1,value2] for key,value1,value2 in heating_compare]
    cooling_compare = [[key,value1,value2] for key,value1,value2 in cooling_compare]
    output['mylist_proposed'] = mylist_proposed
    output['heating_compare'] = heating_compare
    output['cooling_compare'] = cooling_compare

  

    print('done processing results')

    db_list = ['cooling_compare','heating_compare','Total_Savings','Annual_Savings','Heating_Base','Heating_Proposed','Heating_Savings','Cooling_Base','Cooling_Proposed','Cooling_Savings','Interior_Equipment_Base','Interior_Equipment_Proposed','Interior_Equipment_Savings',"Interior_Lighting_Base","Interior_Lighting_Proposed",
        "Interior_Lighting_Savings",'Fans_Base','Fans_Proposed','Fans_Savings',
        "Pumps_Base","Pumps_Proposed","Pumps_Savings","Heat_Rejection_Base",
        "Heat_Rejection_Proposed","Heat_Rejection_Savings","Total_Base","Total_Proposed","Total_Savings_Percent","heat_save","cool_save","total_save",
        "heat_save_area","cool_save_area","total_save_area","heat_save_cost","cool_save_cost","total_save_cost"]    


    for value in db_list:
        setattr(form_detailed_data,value,output[value])
    
    form_detailed_data.heating_compare = json.dumps(heating_compare)
    form_detailed_data.cooling_compare = json.dumps(cooling_compare)
    form_detailed_data.save()
    emailid = form_detailed_data.emailid
    
    if emailid:
        subject = 'Cool Roof Calculator results'
        message = 'http://localhost:8000/display_results/' + str(pk) + "/"
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [emailid]

        print("\n======== Email Sending Debug ========")
        print(f"Subject: {subject}")
        print(f"Message: {message}")
        print(f"Email From: {email_from}")
        print(f"Recipient List: {recipient_list}")
        
        try:
            result = send_mail(subject, message, email_from, recipient_list, fail_silently=False)
            print(f"send_mail result: {result}")  # Should be 1 if successful
            if result == 1:
                print("✅ Email sent successfully!")
            else:
                print("❌ Email failed to send (return value 0).")
        except Exception as e:
            print("❌ Email sending failed:", e)



if __name__ == "__main__":
    #run_simulation(1)
    run_simulation_parametric(1)