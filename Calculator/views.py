from threading import Thread
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
#from forms import Simple
from Calculator.models import Simple
#from django_q.tasks import async_task
from Calculator.models import Detailed_Data
from Calculator.models import Parametric_Data
from .tasks import run_simulation, run_simulation_simple, run_simulation_parametric
import uuid
import time
from time import sleep
import datetime
import math
import os, errno, sys
import shlex, subprocess
from django.conf import settings
from importlib import import_module
from django.conf import settings
from string import Template
from bs4 import BeautifulSoup,Comment
from django.contrib.auth.models import User
import requests
import csv
import json
from celery.result import AsyncResult
import pdb
from django.core.mail import send_mail , EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from django.http import  JsonResponse
#from django_q.models import Task


# from django.contrib.auth import logout
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Create your views here.

#For Simple inputs form func()
def simple(request):

    pk = None 
    formdata = Simple(request.POST)
    
    msg = ""
    try:
          # GENERATES UNIQUE CODE FOR WORKING DIRECTORY OF USER FOR A PARTICULAR SIMULATION
        file_uuid = str(uuid.uuid1())
        # Request method : POST
        Location = request.POST["Location"]
       
        Building_type = request.POST["Building_type"]
        Roof_area = request.POST.get("Roof_area","130")
        Roof_type = request.POST["Roof_type"]
        Radiant_barrier = request.POST["Radiant_barrier"]
        basecase = request.POST["basecase"]
        proposedcase = request.POST["proposedcase"]
        HVAC_details = request.POST["HVAC_details"]
        Electricity = request.POST["Electricity"]
        print("Electricity",Electricity, "Roof_area",Roof_area)
        user_name = request.POST["user_name"]
        print("user_name",user_name)
        emailid = request.POST["emailid"]
        # Weather file Location for the E+ Simulation
        
        weather_file = os.path.join(BASE_DIR,"static/WeatherData/")+Location+".epw" 
        
        # DEFAULT VALUES for EMMISIVITY AND REFLECTIVTIY
        basecasee = "0.87"
        proposedcasee = "0.87"
        #  SETTING EMMISIVITY AND REFLECTIVTIY VALUES of BASE AND PROPOSED 
        if (basecase == "0.23"):
            basecasee = "0.87"

        elif (basecase == "0.22"):
            basecasee = "0.91"

        elif (basecase == "0.25"):
            basecasee = "0.90"

        elif (basecase == "0.33"):
            basecasee = "0.90"

        elif (basecase == "0.34"):
            basecasee = "0.90"

        elif (basecase == "0.61"):
            basecasee = "0.25"

        elif (basecase == "0.65"):
            basecasee = "0.90"

        elif (basecase == "0.67"):
            basecasee = "0.85"

        elif (basecase == "0.69"):
            basecasee = "0.87"

        elif (basecase == "0.73"):
            basecasee = "0.90"

        elif (basecase == "0.80"):
            basecasee = "0.91"

        elif (basecase == "0.83"):
            basecasee = "0.92"

        elif (basecase == "0.85"):
            basecasee = "0.91"

        if (proposedcase == "0.23"):
            proposedcasee = "0.87"

        elif (proposedcase == "0.22"):
            proposedcasee = "0.91"

        elif (proposedcase == "0.25"):
            proposedcasee = "0.90"

        elif (proposedcase == "0.33"):
            proposedcasee = "0.90"

        elif (proposedcase == "0.34"):
            proposedcasee = "0.90"

        elif (proposedcase == "0.61"):
            proposedcasee = "0.25"

        elif (proposedcase == "0.65"):
            proposedcasee = "0.90"

        elif (proposedcase == "0.67"):
            proposedcasee = "0.85"

        elif (proposedcase == "0.69"):
            proposedcasee = "0.87"

        elif (proposedcase == "0.73"):
            proposedcasee = "0.90"

        elif (proposedcase == "0.80"):
            proposedcasee = "0.91"

        elif (proposedcase == "0.83"):
            proposedcasee = "0.92"

        elif (proposedcase == "0.85"):
            proposedcasee = "0.91"

        lpd = "10.8"
        epd = "16.15"
        areaoutofrange = ""
  


        if (Electricity == ""):
            Electricity = 6

        building_desc = "Coolroof_IDF"

        if (Roof_area==""):
            Roof_area = 130

        length = width = math.sqrt(int(Roof_area))
        
        solarAbBase = visibleAbBase = 1 - float(basecase)

        solarAbProposed = visibleAbProposed = 1 - float(proposedcase)
        thermalAbBase = basecasee
        thermalAbProposed = proposedcasee 
        
        # Fenestrations calculations
        OriginZ1_x = 0
        OriginZ1_y = 0
        OriginZ1_z = 0   # Zone 1 and 4 have the same origin
        OriginZ2_x = length
        OriginZ2_y = 0
        OriginZ2_z = 0
        OriginZ3_x = 4.57
        OriginZ3_y = width - 4.57
        OriginZ3_z = 0
        OriginZ5_x = 4.57
        OriginZ5_y = 4.57
        OriginZ5_z = 0
        ftoFHeight = 3.5

        #Glazing percentage
        glazing_front = 30
        glazing_back = 30 
        glazing_left = 30 
        glazing_right = 30 
        volume = ftoFHeight * float(Roof_area)
        
        
        volumeLength = round(ftoFHeight * 4.57 * (length-4.57), 4)
        volumeWidth = round(ftoFHeight * 4.57 * (width-4.57), 4)
        volumeCenter = round(ftoFHeight * (length-9.14) * (width-9.14), 4)
        perimeterLength = 4.5700
        perimeterLengthNegative = -4.5700
        LengthMinusPerimitersBoth = length - 4.57 - .05
        NegativePerimPlusFenesPerim = -4.57 + .05
        glazingHeightFront = round((((ftoFHeight * length) *glazing_front) / 100) / (length-.1), 4)
        
        if (glazingHeightFront < (ftoFHeight-.8)):
            frontFenestZCoordUpper = .75 +glazingHeightFront
            frontFenestZCoordLower = .75
        else:
            frontFenestZCoordUpper = ftoFHeight - .05
            frontFenestZCoordLower = ftoFHeight - .05 - glazingHeightFront
            if (frontFenestZCoordLower < .05):
                frontFenestZCoordLower = .05
        glazingHeightLeft = round((((ftoFHeight * width) *glazing_left) / 100) / (width-.1), 4)
        if (glazingHeightLeft < (ftoFHeight-.8)):
            leftFenestZCoordUpper = .75 +glazingHeightLeft
            leftFenestZCoordLower = .75
        else:
            leftFenestZCoordUpper = ftoFHeight - .05
            leftFenestZCoordLower = ftoFHeight - .05 - glazingHeightLeft
            if (leftFenestZCoordLower < .05):
                leftFenestZCoordLower = .05
        glazingHeightBack = round((((ftoFHeight * length) *glazing_back) / 100) / (length-.1), 4)
        if (glazingHeightBack < (ftoFHeight-.8)):
            backFenestZCoordUpper = .75 +glazingHeightBack
            backFenestZCoordLower = .75
        else:
            backFenestZCoordUpper = ftoFHeight - .05
            backFenestZCoordLower = ftoFHeight - .05 - glazingHeightBack
            if (backFenestZCoordLower < .05):
                backFenestZCoordLower = .05
        glazingHeightRight = round((((ftoFHeight * width) *glazing_right) / 100) / (width-.1), 4)
        if (glazingHeightRight < (ftoFHeight-.8)):
            rightFenestZCoordUpper = .75 +glazingHeightRight
            rightFenestZCoordLower = .75
        else:
            rightFenestZCoordUpper = ftoFHeight - .05
            rightFenestZCoordLower = ftoFHeight - .05 - glazingHeightRight
            if (rightFenestZCoordLower < .05):
                rightFenestZCoordLower = .05
        
        # Radiant Barrier System
        rad_layer_abs = "0.9"
        thermalAbBase =rad_layer_abs
        thermalAbProposed =rad_layer_abs
        # Dealing with roof type
        construction = ""
        material = ""
        if (Roof_type == "insulated"):

                  material = """
    Material,
    Roof Plaster,            !- Name
    Rough,                   !- Roughness
    0.012,                    !- Thickness {m}
    0.88,                    !- Conductivity {W/m-K}
    2800,                    !- Density {kg/m3}
    896,                     !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.7,                     !- Solar Absorptance
    0.7;                     !- Visible Absorptance
    Material,
    Concrete Reinforced (2% Steel),  !- Name
    MediumRough,             !- Roughness
    0.152,                   !- Thickness {m}
    2.5,                     !- Conductivity {W/m-K}
    2400,                    !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.6,                     !- Solar Absorptance
    0.6;                     !- Visible Absorptance
    Material,
    Gypsum Plasterboard,     !- Name
    Rough,                   !- Roughness
    0.012,                   !- Thickness {m}
    0.25,                    !- Conductivity {W/m-K}
    900,                     !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    $rad_layer_abs,                     !- Thermal Absorptance
    0.5,                     !- Solar Absorptance
    0.5;                     !- Visible Absorptance
    Material:NoMass,
    Insulation,              !- Name
    MediumRough,             !- Roughness
    3.5,                     !- Thermal Resistance {m2-K/W}
    0.9,                     !- Thermal Absorptance
    0.7,                     !- Solar Absorptance
    0.7;                     !- Visible Absorptance
                  """
                  construction = """
    Construction,
          Roof,                    !- Name
          Roof Coating,            !- Outside Layer
          Roof Plaster,            !- Layer 2
          Insulation,              !- Layer 3
          Concrete Reinforced (2% Steel),  !- Layer 4
          Gypsum Plasterboard  """

        elif (Roof_type == "uninsulated"):

                  material = """
    Material,
    Roof Plaster,            !- Name
    Rough,                   !- Roughness
    0.012,                    !- Thickness {m}
    0.88,                    !- Conductivity {W/m-K}
    2800,                    !- Density {kg/m3}
    896,                     !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.7,                     !- Solar Absorptance
    0.7;                     !- Visible Absorptance
    Material,
    Concrete Reinforced (2% Steel),  !- Name
    MediumRough,             !- Roughness
    0.152,                   !- Thickness {m}
    2.5,                     !- Conductivity {W/m-K}
    2400,                    !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.6,                     !- Solar Absorptance
    0.6;                     !- Visible Absorptance
    Material,
    Gypsum Plasterboard,     !- Name
    Rough,                   !- Roughness
    0.012,                   !- Thickness {m}
    0.25,                    !- Conductivity {W/m-K}
    900,                     !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    $rad_layer_abs,                     !- Thermal Absorptance
    0.5,                     !- Solar Absorptance
    0.5;                     !- Visible Absorptance
    Material:NoMass,
    Insulation,              !- Name
    MediumRough,             !- Roughness
    0.001,                   !- Thermal Resistance {m2-K/W}
    0.9,                     !- Thermal Absorptance
    0.7,                     !- Solar Absorptance
    0.7;                     !- Visible Absorptance """
                  construction = """
    Construction,
        Roof,                    !- Name
        Roof Coating,            !- Outside Layer
        Roof Plaster,            !- Layer 2
        Insulation,              !- Layer 3
        Concrete Reinforced (2% Steel),  !- Layer 4
        Gypsum Plasterboard  """

        elif (Roof_type == "material3"):

                  material = """
    Material,
    Roof Plaster,            !- Name
    Rough,                   !- Roughness
    0.012,                    !- Thickness {m}
    0.88,                    !- Conductivity {W/m-K}
    2800,                    !- Density {kg/m3}
    896,                     !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.7,                     !- Solar Absorptance
    0.7;                     !- Visible Absorptance
    Material,
    Concrete Reinforced (2% Steel),  !- Name
    MediumRough,             !- Roughness
    0.152,                   !- Thickness {m}
    2.5,                     !- Conductivity {W/m-K}
    2400,                    !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.6,                     !- Solar Absorptance
    0.6;                     !- Visible Absorptance
    Material,
    Gypsum Plasterboard,     !- Name
    Rough,                   !- Roughness
    0.012,                   !- Thickness {m}
    0.25,                    !- Conductivity {W/m-K}
    900,                     !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    $rad_layer_abs,                     !- Thermal Absorptance
    0.5,                     !- Solar Absorptance
    0.5;                     !- Visible Absorptance
    Material:NoMass,
    Insulation,              !- Name
    MediumRough,             !- Roughness
    3.5,                     !- Thermal Resistance {m2-K/W}
    0.9,                     !- Thermal Absorptance
    0.7,                     !- Solar Absorptance
    0.7;                     !- Visible Absorptance

                    """
                  construction = """
    Construction,
      Roof,                    !- Name
      Roof Coating,            !- Outside Layer
      Roof Plaster,            !- Layer 2
      Concrete Reinforced (2% Steel),  !- Layer 4
      Gypsum Plasterboard  """
                    
        elif (Roof_type == "material4"):
                        
                  material = """
    Material,
    Roof plaster,            !- Name
    Rough,                   !- Roughness
    0.012,                    !- Thickness {m}
    0.88,                    !- Conductivity {W/m-K}
    2800,                    !- Density {kg/m3}
    896,                     !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.7,                     !- Solar Absorptance
    0.7;                     !- Visible Absorptance
    Material,
    Concrete Reinforced (2% Steel),  !- Name
    MediumRough,             !- Roughness
    0.152,                   !- Thickness {m}
    2.5,                     !- Conductivity {W/m-K}
    2400,                    !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.6,                     !- Solar Absorptance
    0.6;                     !- Visible Absorptance
    Material,
    Gypsum Plasterboard,     !- Name
    Rough,                   !- Roughness
    0.012,                   !- Thickness {m}
    0.25,                    !- Conductivity {W/m-K}
    900,                     !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    $rad_layer_abs,                     !- Thermal Absorptance
    0.5,                     !- Solar Absorptance
    0.5;                     !- Visible Absorptance
    Material:NoMass,
    Insulation,              !- Name
    MediumRough,             !- Roughness
    3.5,                     !- Thermal Resistance {m2-K/W}
    0.9,                     !- Thermal Absorptance
    0.7,                     !- Solar Absorptance
    0.7;                     !- Visible Absorptance
                        """
                  construction = """
    Construction,
    Roof,                    !- Name
    Roof Coating,            !- Outside Layer
    Roof Plaster,            !- Layer 2
    Concrete Reinforced (2% Steel),  !- Layer 4
    Gypsum Plasterboard  """

        elif (Roof_type == "material5"):
                  material = """
    Material,
    Roof plaster,            !- Name
    Rough,                   !- Roughness
    0.012,                    !- Thickness {m}
    0.88,                    !- Conductivity {W/m-K}
    2800,                    !- Density {kg/m3}
    896,                     !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.7,                     !- Solar Absorptance
    0.7;                     !- Visible Absorptance
    Material,
    Concrete Reinforced (2% Steel),  !- Name
    MediumRough,             !- Roughness
    0.152,                   !- Thickness {m}
    2.5,                     !- Conductivity {W/m-K}
    2400,                    !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.6,                     !- Solar Absorptance
    0.6;                     !- Visible Absorptance
    Material,
    Gypsum Plasterboard,     !- Name
    Rough,                   !- Roughness
    0.012,                   !- Thickness {m}
    0.25,                    !- Conductivity {W/m-K}
    900,                     !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    $rad_layer_abs,                     !- Thermal Absorptance
    0.5,                     !- Solar Absorptance
    0.5;                     !- Visible Absorptance
    Material:NoMass,
    Insulation,              !- Name
    MediumRough,             !- Roughness
    3.5,                     !- Thermal Resistance {m2-K/W}
    0.9,                     !- Thermal Absorptance
    0.7,                     !- Solar Absorptance
    0.7;                     !- Visible Absorptance
                            """
                  construction = """
    Construction,
    Roof,                    !- Name
    Roof Coating,            !- Outside Layer
    Roof Plaster,            !- Layer 2
    Concrete Reinforced (2% Steel),  !- Layer 4
    Gypsum Plasterboard  """

        elif (Roof_type == "material6"):

                  material = """
    Material,
    Roof plaster,            !- Name
    Rough,                   !- Roughness
    0.012,                    !- Thickness {m}
    0.88,                    !- Conductivity {W/m-K}
    2800,                    !- Density {kg/m3}
    896,                     !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.7,                     !- Solar Absorptance
    0.7;                     !- Visible Absorptance
    Material,
    Concrete Reinforced (2% Steel),  !- Name
    MediumRough,             !- Roughness
    0.152,                   !- Thickness {m}
    2.5,                     !- Conductivity {W/m-K}
    2400,                    !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.6,                     !- Solar Absorptance
    0.6;                     !- Visible Absorptance
    Material,
    Gypsum Plasterboard,     !- Name
    Rough,                   !- Roughness
    0.012,                   !- Thickness {m}
    0.25,                    !- Conductivity {W/m-K}
    900,                     !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    $rad_layer_abs,                     !- Thermal Absorptance
    0.5,                     !- Solar Absorptance
    0.5;                     !- Visible Absorptance
    Material:NoMass,
    Insulation,              !- Name
    MediumRough,             !- Roughness
    3.5,                     !- Thermal Resistance {m2-K/W}
    0.9,                     !- Thermal Absorptance
    0.7,                     !- Solar Absorptance
    0.7;                     !- Visible Absorptance

                                """
                  construction = """
    Construction,
    Roof,                    !- Name
    Roof Coating,            !- Outside Layer
    Roof Plaster,            !- Layer 2
    Insulation,              !- Layer 3
    Concrete Reinforced (2% Steel),  !- Layer 4
    Gypsum Plasterboard """

        elif (Roof_type == "material7"):

                  material = """
    Material,
    Roof plaster,            !- Name
    Rough,                   !- Roughness
    0.012,                    !- Thickness {m}
    0.88,                    !- Conductivity {W/m-K}
    2800,                    !- Density {kg/m3}
    896,                     !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.7,                     !- Solar Absorptance
    0.7;                     !- Visible Absorptance
    Material,
    Concrete Reinforced (2% Steel),  !- Name
    MediumRough,             !- Roughness
    0.152,                   !- Thickness {m}
    2.5,                     !- Conductivity {W/m-K}
    2400,                    !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.6,                     !- Solar Absorptance
    0.6;                     !- Visible Absorptance
    Material,
    Gypsum Plasterboard,     !- Name
    Rough,                   !- Roughness
    0.012,                   !- Thickness {m}
    0.25,                    !- Conductivity {W/m-K}
    900,                     !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    $rad_layer_abs,                     !- Thermal Absorptance
    0.5,                     !- Solar Absorptance
    0.5;                     !- Visible Absorptance
    Material:NoMass,
    Insulation,              !- Name
    MediumRough,             !- Roughness
    3.5,                     !- Thermal Resistance {m2-K/W}
    0.9,                     !- Thermal Absorptance
    0.7,                     !- Solar Absorptance
    0.7;                     !- Visible Absorptance
                                    """
                  construction = """
    Construction,
    Roof,                    !- Name
    Roof Coating,            !- Outside Layer
    Roof Plaster,            !- Layer 2
    Insulation,              !- Layer 3
    Concrete Reinforced (2% Steel),  !- Layer 4
    Gypsum Plasterboard  """

        elif (Roof_type == "material8"):

                  material = """
    Material,
    Roof plaster,            !- Name
    Rough,                   !- Roughness
    0.012,                    !- Thickness {m}
    0.88,                    !- Conductivity {W/m-K}
    2800,                    !- Density {kg/m3}
    896,                     !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.7,                     !- Solar Absorptance
    0.7;                     !- Visible Absorptance
    Material,
    Concrete Reinforced (2% Steel),  !- Name
    MediumRough,             !- Roughness
    0.152,                   !- Thickness {m}
    2.5,                     !- Conductivity {W/m-K}
    2400,                    !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.6,                     !- Solar Absorptance
    0.6;                     !- Visible Absorptance
    Material,
    Gypsum Plasterboard,     !- Name
    Rough,                   !- Roughness
    0.012,                   !- Thickness {m}
    0.25,                    !- Conductivity {W/m-K}
    900,                     !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    $rad_layer_abs,                     !- Thermal Absorptance
    0.5,                     !- Solar Absorptance
    0.5;                     !- Visible Absorptance
    Material:NoMass,
    Insulation,              !- Name
    MediumRough,             !- Roughness
    3.5,                     !- Thermal Resistance {m2-K/W}
    0.9,                     !- Thermal Absorptance
    0.7,                     !- Solar Absorptance
    0.7;                     !- Visible Absorptance

                                        """
                  construction = """
    Construction,
    Roof,                    !- Name
    Roof Coating,            !- Outside Layer
    Roof Plaster,            !- Layer 2
    Insulation,              !- Layer 3
    Concrete Reinforced (2% Steel),  !- Layer 4
    Gypsum Plasterboard   """

        elif (Roof_type == "material9"):

                  material = """
    Material,
    Roof plaster,            !- Name
    Rough,                   !- Roughness
    0.012,                    !- Thickness {m}
    0.88,                    !- Conductivity {W/m-K}
    2800,                    !- Density {kg/m3}
    896,                     !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.7,                     !- Solar Absorptance
    0.7;                     !- Visible Absorptance
    Material,
    Concrete Reinforced (2% Steel),  !- Name
    MediumRough,             !- Roughness
    0.152,                   !- Thickness {m}
    2.5,                     !- Conductivity {W/m-K}
    2400,                    !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.6,                     !- Solar Absorptance
    0.6;                     !- Visible Absorptance
    Material,
    Gypsum Plasterboard,     !- Name
    Rough,                   !- Roughness
    0.012,                   !- Thickness {m}
    0.25,                    !- Conductivity {W/m-K}
    900,                     !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    $rad_layer_abs,                     !- Thermal Absorptance
    0.5,                     !- Solar Absorptance
    0.5;                     !- Visible Absorptance
    Material:NoMass,
    Insulation,              !- Name
    MediumRough,             !- Roughness
    3.5,                     !- Thermal Resistance {m2-K/W}
    0.9,                     !- Thermal Absorptance
    0.7,                     !- Solar Absorptance
    0.7;                     !- Visible Absorptance

                                            """
                  construction = """
    Construction,
    Roof,                    !- Name
    Roof Coating,            !- Outside Layer
    Roof Plaster,            !- Layer 2
    Insulation,              !- Layer 3
    Concrete Reinforced (2% Steel),  !- Layer 4
    Gypsum Plasterboard   """

        elif (Roof_type == "material10"):

                  material = """
    Material,
    Roof plaster,            !- Name
    Rough,                   !- Roughness
    0.012,                    !- Thickness {m}
    0.88,                    !- Conductivity {W/m-K}
    2800,                    !- Density {kg/m3}
    896,                     !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.7,                     !- Solar Absorptance
    0.7;                     !- Visible Absorptance
    Material,
    Concrete Reinforced (2% Steel),  !- Name
    MediumRough,             !- Roughness
    0.152,                   !- Thickness {m}
    2.5,                     !- Conductivity {W/m-K}
    2400,                    !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.6,                     !- Solar Absorptance
    0.6;                     !- Visible Absorptance
    Material,
    Gypsum Plasterboard,     !- Name
    Rough,                   !- Roughness
    0.012,                   !- Thickness {m}
    0.25,                    !- Conductivity {W/m-K}
    900,                     !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    $rad_layer_abs,                     !- Thermal Absorptance
    0.5,                     !- Solar Absorptance
    0.5;                     !- Visible Absorptance
    Material:NoMass,
    Insulation,              !- Name
    MediumRough,             !- Roughness
    3.5,                     !- Thermal Resistance {m2-K/W}
    0.9,                     !- Thermal Absorptance
    0.7,                     !- Solar Absorptance
    0.7;                     !- Visible Absorptance
    """
                  construction = """
    Construction,
    Roof,                    !- Name
    Roof Coating,            !- Outside Layer
    Roof Plaster,            !- Layer 2
    Insulation,              !- Layer 3
    Concrete Reinforced (2% Steel),  !- Layer 4
    Gypsum Plasterboard   """
        material_rad = """
    Material,
    Radiant Barrier,         !- Name
    Rough,                   !- Roughness
    0.012,                   !- Thickness {m}
    0.25,                    !- Conductivity {W/m-K}
    900,                     !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    0.2,                     !- Thermal Absorptance
    0.3,                     !- Solar Absorptance
    0.3;                     !- Visible Absorptance
                                            """
        s = Template(material)
        material = s.substitute(rad_layer_abs=rad_layer_abs)
        baseMaterial =material
        proposedMaterial =material
        baseConstruction =construction
        baseConstruction =baseConstruction + ";     !- Layer 5\n"
        proposedConstruction =construction
        if (Radiant_barrier == "ON"):
            proposedMaterial = proposedMaterial + material_rad
            proposedConstruction=proposedConstruction + ";     !- Layer 5\n"
            proposedConstruction = proposedConstruction + "    Radiant Barrier"
        
        if (Radiant_barrier == "ON"):
            proposedConstruction = proposedConstruction + ";         !-Layer 6\n"
        else:
            proposedConstruction = proposedConstruction + ";     !- Layer 5\n"        
        # Create directories
        static_dir = settings.STATICFILES_DIRS[1]
        #static_dir = os.path.join(BASE_DIR, 'static')
        try:
            folder = os.mkdir(os.path.join(static_dir,"model_idf",file_uuid))
            base_folder = os.mkdir(os.path.join(static_dir,"model_idf",file_uuid,"base"))
            proposed_folder = os.mkdir(os.path.join(static_dir,"model_idf",file_uuid,"proposed"))
            folder2 = os.mkdir(os.path.join(BASE_DIR,"templates","html_dir",file_uuid))
            base_html_folder = os.mkdir(os.path.join(BASE_DIR,"templates","html_dir",file_uuid,"base"))
            proposed_html_folder = os.mkdir(os.path.join(BASE_DIR,"templates","html_dir",file_uuid,"proposed"))
        except OSError as e:
            if e.errno != errno.EEXIST:
                # directory already exists
                pass
            else:
                print(e)
       # Dealing With Schedules
        scheduleClass = ""
        hvac_string = ""
        modelTemplate = ""
        if (Building_type == "office"):
            if (HVAC_details == "uc"):
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Office/Main_Office_UC.idf")            
            else:
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Office/Office_Main.idf")
            if (HVAC_details == "ptac"):              
                fname = os.path.join(BASE_DIR, 'static/idfsnippets/Office/Schedule_Office_PTHP.txt')

                fptr = open(fname, "r") or exit("Unable to open file!")                
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Office/HVAC_Office_PTHP.txt")
                
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                
                file1.close()
            elif (HVAC_details == "pszhp"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Office/Schedule_Office_Others_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Office/HVAC_Office_PSZHP_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()
            elif (HVAC_details == "watercooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Office/Schedule_Office_Others_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Office/HVAC_Office_Watercooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()
            elif (HVAC_details == "aircooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Office/Schedule_Office_Others_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Office/HVAC_Office_Aircooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()
            elif (HVAC_details == "uc"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Office/Schedule_Office_UC_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Office/HVAC_Office_UC_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()
        elif (Building_type == "institutional"):
        #	write_trace("Got insti");
            if (HVAC_details == "uc"):
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Institute/Main_Institute_UC.idf")
            else:
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Institute/Institute_Main.idf")
            if (HVAC_details == "ptac"):
        
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Institute/Schedule_Institute_Others_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Institute/HVAC_Institute_PTHP_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()
        
            elif (HVAC_details == "pszhp"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Institute/Schedule_Institute_Others_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Institute/HVAC_Institute_PSZHP_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "watercooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Institute/Schedule_Institute_Others_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Institute/HVAC_Institute_Watercooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "aircooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Institute/Schedule_Institute_Aircooled_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Institute/HVAC_Institute_Aircooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "uc"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Institute/Schedule_Institute_UC_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Institute/HVAC_Institute_UC_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()
        elif (Building_type == "retail"):
                
            if (HVAC_details == "uc"):
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Retail/Main_Retail_UC.idf")
            
            else:
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Retail/Retail_Main.idf")
            
            if (HVAC_details == "ptac"):

                fname = os.path.join(BASE_DIR,"static/idfsnippets/Retail/Schedule_Retail_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Retail/HVAC_Retail_PTHP_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "pszhp"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Retail/Schedule_Retail_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Retail/HVAC_Retail_PSZHP_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "watercooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Retail/Schedule_Retail_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Retail/HVAC_Retail_Watercooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "aircooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Retail/Schedule_Retail_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Retail/HVAC_Retail_Aircooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "uc"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Retail/Schedule_Retail_UC.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Retail/HVAC_Retail_UC.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

                
        elif (Building_type == "residentialallday"):
            if (HVAC_details == "uc"):
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/Main_Residential_24H_UC.idf")
            
            else:
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/Residential_24_Main.idf")
            
            if (HVAC_details == "ptac"):
            
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/Schedule_Residential_24_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/HVAC_Residential_24_PTHP_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "pszhp"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/Schedule_Residential_24_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/HVAC_Residential_24_PSZHP_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "watercooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/Schedule_Residential_24_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/HVAC_Residential_24_Watercooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "aircooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/Schedule_Residential_24_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/HVAC_Residential_24_Aircooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "uc"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/Schedule_Residential_24_UC.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/HVAC_Residential_24H_UC.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

                
        elif (Building_type == "residentialonlynight"):
                
            if (HVAC_details == "uc"):
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/Main_Residential_Night_UC.idf")
            
            else:
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/Residential_Night_Main.idf")
            
            if (HVAC_details == "ptac"):

                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/Schedule_Residential_Night_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/HVAC_Residential_Night_PTHP_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()
            
            elif (HVAC_details == "pszhp"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/Schedule_Residential_Night_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/HVAC_Residential_Night_PSZHP_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "watercooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/Schedule_Residential_Night_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/HVAC_Residential_Night_Watercooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "aircooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/Schedule_Residential_Night_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/HVAC_Residential_Night_Aircooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "uc"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/Schedule_Residential_Night_UC.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/HVAC_Residential_Night_UC.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

        # Setting up the Appendix G Type                
        appendix_G = 0
        if (HVAC_details == "pszhp"):
            appendix_G = 5
        elif (HVAC_details == "ptac"):
            appendix_G = 3
        elif (HVAC_details == "watercooled" or HVAC_details == "aircooled"):
            appendix_G =9
        elif (HVAC_details == "uc"):
            appendix_G = 3
            
        dNt =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        file1 = open(modelTemplate, "r") or sys.exit("can't open HVAC_details, scheduleClass, modelTemplate for reading")
        
        #   Read the template and create base idf file
        theData = file1.read()

        theData = theData.replace('%ScheduleString%',scheduleClass)
        
        theData = theData.replace('%NegativePerimPlusFenesPerim%',str(NegativePerimPlusFenesPerim))
        
        theData = theData.replace('%LengthMinusPerimitersBoth%',str(LengthMinusPerimitersBoth))

        theData = theData.replace('%PerimeterNeg%',str(perimeterLengthNegative))
        theData = theData.replace('%Perimeter%',str(perimeterLength))              
        theData = theData.replace('%building_desc%',building_desc)
        theData = theData.replace('%ThermalAbsorptance%',"0.9")

        theData = theData.replace('%SolarAbsorptance%',str(round(solarAbBase, 3)))
        theData = theData.replace('%VisibleAbsorptance%',str(round(visibleAbBase, 3)))
        theData = theData.replace('%FloorToFloorHeight%',str(ftoFHeight))
        theData = theData.replace('%LengthMinusPerimeterDouble%',str(round(width-9.14, 4)))
        theData = theData.replace('%LengthMinusNinePointOneFour%',str(round(length-9.14, 4)))
        theData = theData.replace('%Width%',str(round(width, 4)))
        theData = theData.replace('%LengthMinusPerimeter%',str(round(width-4.57, 4)))
        theData = theData.replace('%LengthMinusFourPointFiveSeven%',str(round(length-4.57, 4)))
        theData = theData.replace('%leftFenestZCoordLower%',str(round(leftFenestZCoordLower, 4)))
        theData = theData.replace('%frontFenestZCoordUpper%',str(round(frontFenestZCoordUpper, 4)))
        theData = theData.replace('%frontFenestZCoordLower%',str(round(frontFenestZCoordLower, 4)))
        theData = theData.replace('%LengthMinusPointZeroFive%',str(round(length-0.05, 4)))
        
        theData = theData.replace('%rightFenestZCoordUpper%',str(round(rightFenestZCoordUpper, 4)))
        theData = theData.replace('%rightFenestZCoordLower%',str(round(rightFenestZCoordLower, 4)))
        theData = theData.replace('%WidthMinusPointZeroFive%',str(round(width-0.05, 4)))
        theData = theData.replace('%LengthMinusFourPointSixTwo%',str(round(length-4.62, 4)))
        theData = theData.replace('%backFenestZCoordUpper%',str(round(backFenestZCoordUpper, 4)))
        theData = theData.replace('%backFenestZCoordLower%',str(round(backFenestZCoordLower, 4)))
        theData = theData.replace('%leftFenestZCoordUpper%',str(round(leftFenestZCoordUpper, 4)))
        theData = theData.replace('%OriginZ1_x%',str(round(OriginZ1_x, 4)))
        theData = theData.replace('%OriginZ1_y%',str(round(OriginZ1_y, 4)))
        theData = theData.replace('%OriginZ1_z%',str(round(OriginZ1_z, 4)))
        theData = theData.replace('%OriginZ2_x%',str(round(OriginZ2_x, 4)))
        theData = theData.replace('%OriginZ2_y%',str(round(OriginZ2_y, 4)))
        theData = theData.replace('%OriginZ2_z%',str(round(OriginZ2_z, 4)))
        theData = theData.replace('%OriginZ3_x%',str(round(OriginZ3_x, 4)))
        theData = theData.replace('%OriginZ3_y%',str(round(OriginZ3_y, 4)))
        theData = theData.replace('%OriginZ3_z%',str(round(OriginZ3_z, 4)))
        theData = theData.replace('%OriginZ5_x%',str(round(OriginZ5_x, 4)))
        theData = theData.replace('%OriginZ5_y%',str(round(OriginZ5_y, 4)))
        theData = theData.replace('%OriginZ5_z%',str(round(OriginZ5_z, 4)))
        theData = theData.replace('%Volume%',str(round(volume, 4)))
        theData = theData.replace('%Length%',str(round(length, 4)))
        theData = theData.replace('%Width%',str(round(width, 4)))
        theData = theData.replace('%VolumeLength%',str(round(volumeLength, 4)))
        theData = theData.replace('%VolumeWidth%',str(round(volumeWidth, 4)))
        theData = theData.replace('%VolumeCenter%',str(round(volumeCenter, 4)))
        theData = theData.replace('%ThermalAbsorptance%',str(thermalAbBase))
        theData = theData.replace('%LPD%',lpd)
        theData = theData.replace('%EPD%',epd)
        theData = theData.replace('%volumeLength%',str(volumeLength))
        theData = theData.replace('%date_n_time%',str(dNt))
        theData = theData.replace('%site_location%',str(Location))
        theData = theData.replace('%appendix_type%',str(appendix_G))
       
        base_path = os.path.join(static_dir,"model_idf",file_uuid,"base","model.idf")
        
         
        with open(base_path,'w') as file2:

            file2.write(theData)
            file2.write(baseMaterial)
            file2.write(baseConstruction)
            file2.write(hvac_string)

        file2.close()
        file1.close()


        file1 = open(modelTemplate, "r") 
        theData = file1.read()

         #   Read the template and create proposed idf file
        theData = theData.replace('%ScheduleString%',scheduleClass)
        
        theData = theData.replace('%NegativePerimPlusFenesPerim%',str(NegativePerimPlusFenesPerim))
        
        theData = theData.replace('%LengthMinusPerimitersBoth%',str(LengthMinusPerimitersBoth))

        theData = theData.replace('%PerimeterNeg%',str(perimeterLengthNegative))
        theData = theData.replace('%Perimeter%',str(perimeterLength))              
        theData = theData.replace('%building_desc%',building_desc)
        theData = theData.replace('%ThermalAbsorptance%',"0.9")

        theData = theData.replace('%SolarAbsorptance%',str(round(solarAbProposed, 3)))
        theData = theData.replace('%VisibleAbsorptance%',str(round(visibleAbProposed, 3)))
        theData = theData.replace('%FloorToFloorHeight%',str(ftoFHeight))
        theData = theData.replace('%LengthMinusPerimeterDouble%',str(round(width-9.14, 4)))
        theData = theData.replace('%LengthMinusNinePointOneFour%',str(round(length-9.14, 4)))
        theData = theData.replace('%Width%',str(round(width, 4)))
        theData = theData.replace('%LengthMinusPerimeter%',str(round(width-4.57, 4)))
        theData = theData.replace('%LengthMinusFourPointFiveSeven%',str(round(length-4.57, 4)))
        theData = theData.replace('%leftFenestZCoordLower%',str(round(leftFenestZCoordLower, 4)))
        theData = theData.replace('%frontFenestZCoordUpper%',str(round(frontFenestZCoordUpper, 4)))
        theData = theData.replace('%frontFenestZCoordLower%',str(round(frontFenestZCoordLower, 4)))
        theData = theData.replace('%LengthMinusPointZeroFive%',str(round(length-0.05, 4)))
        
        theData = theData.replace('%rightFenestZCoordUpper%',str(round(rightFenestZCoordUpper, 4)))
        theData = theData.replace('%rightFenestZCoordLower%',str(round(rightFenestZCoordLower, 4)))
        theData = theData.replace('%WidthMinusPointZeroFive%',str(round(width-0.05, 4)))
        theData = theData.replace('%LengthMinusFourPointSixTwo%',str(round(length-4.62, 4)))
        theData = theData.replace('%backFenestZCoordUpper%',str(round(backFenestZCoordUpper, 4)))
        theData = theData.replace('%backFenestZCoordLower%',str(round(backFenestZCoordLower, 4)))
        theData = theData.replace('%leftFenestZCoordUpper%',str(round(leftFenestZCoordUpper, 4)))
        theData = theData.replace('%OriginZ1_x%',str(round(OriginZ1_x, 4)))
        theData = theData.replace('%OriginZ1_y%',str(round(OriginZ1_y, 4)))
        theData = theData.replace('%OriginZ1_z%',str(round(OriginZ1_z, 4)))
        theData = theData.replace('%OriginZ2_x%',str(round(OriginZ2_x, 4)))
        theData = theData.replace('%OriginZ2_y%',str(round(OriginZ2_y, 4)))
        theData = theData.replace('%OriginZ2_z%',str(round(OriginZ2_z, 4)))
        theData = theData.replace('%OriginZ3_x%',str(round(OriginZ3_x, 4)))
        theData = theData.replace('%OriginZ3_y%',str(round(OriginZ3_y, 4)))
        theData = theData.replace('%OriginZ3_z%',str(round(OriginZ3_z, 4)))
        theData = theData.replace('%OriginZ5_x%',str(round(OriginZ5_x, 4)))
        theData = theData.replace('%OriginZ5_y%',str(round(OriginZ5_y, 4)))
        theData = theData.replace('%OriginZ5_z%',str(round(OriginZ5_z, 4)))
        theData = theData.replace('%Volume%',str(round(volume, 4)))
        theData = theData.replace('%Length%',str(round(length, 4)))
        theData = theData.replace('%Width%',str(round(width, 4)))
        theData = theData.replace('%VolumeLength%',str(round(volumeLength, 4)))
        theData = theData.replace('%VolumeWidth%',str(round(volumeWidth, 4)))
        theData = theData.replace('%VolumeCenter%',str(round(volumeCenter, 4)))
        theData = theData.replace('%ThermalAbsorptance%',str(thermalAbProposed))
        theData = theData.replace('%LPD%',lpd)
        theData = theData.replace('%EPD%',epd)
        theData = theData.replace('%volumeLength%',str(volumeLength))
        theData = theData.replace('%date_n_time%',str(dNt))
        theData = theData.replace('%site_location%',str(Location))
        theData = theData.replace('%appendix_type%',str(appendix_G))
        #       for proposed
        proposed_path = os.path.join(static_dir,"model_idf",file_uuid,"proposed","model.idf")
        
         
        with open(proposed_path,'w') as file2:

            file2.write(theData)
            file2.write(baseMaterial)
            file2.write(baseConstruction)
            file2.write(hvac_string)

        file2.close()
        file1.close()        
        # Store require values in input_dict (dict type)
        input_dict = {"Location":str(Location), "Building_type":str(Building_type), "Roof_area":str(Roof_area),
        "Radiant_barrier":str(Radiant_barrier), "HVAC_details":str(HVAC_details),"Electricity":str(Electricity),"Normal_Roof":str(basecase),"Cool_roof":str(proposedcase),
        "Roof_type":str(Roof_type),"Normal_Roof_e":str(basecasee),"Cool_roof_e":str(proposedcasee),"emailid":str(emailid)}
        print(json.dumps(input_dict))
        # Caching: Check if the output exists; otherwise, create a new Simple object.

        form_detailed_data = Simple.objects.filter(**input_dict).first()
        if form_detailed_data:
           return redirect('display_results_simple/'+str(form_detailed_data.id)+"/")
        else:
            input_dict['file_uuid'] = file_uuid
            input_dict['username'] = user_name
            form_detailed_data = Simple.objects.create(**input_dict)
            print("New entry created.")
        celery_task = run_simulation_simple.delay(form_detailed_data.pk) 
        form_detailed_data.task_id = celery_task.id
        form_detailed_data.save()
        print('done')
        print(celery_task.id)
        result = AsyncResult(celery_task.id)
        print(f'Current Status: {result.status}')
        print(celery_task.ready())
        pk = form_detailed_data.id
        return postdata_loader_simple(request, pk)
    except Exception as e:
        print(f"Error occurred: {e}")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error details: {exc_type}, {fname}, {exc_tb.tb_lineno}")
        
        # Return a generic error message and try to reload the form data if needed
        #pk = form_detailed_data.pk if 'form_detailed_data' in locals() and form_detailed_data else None
        return postdata_loader_simple(request, None)

#For Simple inputs form func()
def detailed(request):
    pk = None
    msg = ""
    try:
        # GENERATES UNIQUE CODE FOR WORKING DIRECTORY OF USER FOR A PARTICULAR SIMULATION
        file_uuid = str(uuid.uuid1())
        Location = request.POST["Location"]
        Building_type = request.POST["Building_type"]
        # Roof_area = request.POST["Roof_area"]
        Roof_area = request.POST.get("Roof_area","130")
        
        layer1 = request.POST["layer1"]
        layer2 = request.POST["layer2"]
        layer3 = request.POST["layer3"]
        layer4 = request.POST["layer4"]

        Radiant_barrier = request.POST["Radiant_barrier"]

        Reflectivity_base = request.POST["reflectivity_base"]
        Emissivity_base = request.POST["emissivity_base"]
        Cost_base = request.POST["cost_base"]
        Life_base = request.POST["life_base"]

        Reflectivity_proposed = request.POST["reflectivity_proposed"]
        Emissivity_proposed = request.POST["emissivity_proposed"]
        Cost_proposed = request.POST["cost_proposed"]
        Life_proposed = request.POST["life_proposed"]

        HVAC_details = request.POST["HVAC_details"]
        System_cop = request.POST["system_cop"]
        Lighting_power = request.POST["lighting_power"]
        Equipment_power = request.POST["equipment_power"]
        win_area_north = request.POST["win_area_north"]
        win_area_south = request.POST["win_area_south"]
        win_area_east = request.POST["win_area_east"]
        win_area_west = request.POST["win_area_west"]
        
        Electricity = request.POST["Electricity"]
        emailid = request.POST["emailid1"]
        user_name = request.POST["user_name"]

        if (Electricity == ""):
            Electricity = 6
        building_desc = "Coolroof_IDF"
        if (Roof_area == ""):
            Roof_area = 130
        if (Reflectivity_base == ""):
            Reflectivity_base = 0.3
        if(Emissivity_base == ""):
            Emissivity_base = 0.9
        if(Cost_base == ""):
            Cost_base = 200
        if (Life_base == ""):
            Life_base = 10
        if (Reflectivity_proposed == ""):
            Reflectivity_proposed = 0.7
        if (Emissivity_proposed == ""):
            Emissivity_proposed = 0.9
        if (Cost_proposed == ""):
            Cost_proposed = 500
        if (Life_proposed == ""):
            Life_proposed = 5
        if (System_cop == ""):
            System_cop = 3
        if (Lighting_power == ""):
            Lighting_power = 10.8
        if (Equipment_power == ""):
            Equipment_power = 16.5
        if (win_area_north == ""):
            win_area_north = 11.97
        if (win_area_south == ""):
            win_area_south = 11.97
        if(win_area_east == ""):
            win_area_east = 11.97
        if (win_area_west == ""):
            win_area_west = 11.97
        weather_file = os.path.join(BASE_DIR,"static/WeatherData/")+Location+".epw"                                                                                                                       
        length = width = math.sqrt(int(Roof_area))
        solarAbBase = visibleAbBase = 1 - float(Reflectivity_base)
        solarAbProposed = visibleAbProposed = 1 - float(Reflectivity_proposed)
        thermalAbBase = float(Emissivity_base)
        thermalAbProposed = float(Emissivity_proposed)
        OriginZ1_x = 0
        OriginZ1_y = 0
        OriginZ1_z = 0  
        OriginZ2_x = float(length)
        OriginZ2_y = 0
        OriginZ2_z = 0
        OriginZ3_x = 4.57
        OriginZ3_y = float(width) - 4.57
        OriginZ3_z = 0
        OriginZ5_x = 4.57
        OriginZ5_y = 4.57
        OriginZ5_z = 0
        ftoFHeight = 3.5
        glazing_front = float(win_area_north)
        glazing_back = float(win_area_south)
        glazing_left = float(win_area_west)
        glazing_right = float(win_area_east)
        volume = ftoFHeight * float(Roof_area)
        
        
        volumeLength = round(ftoFHeight * 4.57 * (length-4.57), 4)
        volumeWidth = round(ftoFHeight * 4.57 * (width-4.57), 4)
        volumeCenter = round(ftoFHeight * (length-9.14) * (width-9.14), 4)
        perimeterLength = 4.5700
        perimeterLengthNegative = -4.5700
        LengthMinusPerimitersBoth = length - 4.57 - .05
        NegativePerimPlusFenesPerim = -4.57 + .05
        glazingHeightFront = round((((ftoFHeight * length) *glazing_front) / 100) / (length-.1), 4)
        
        if (glazingHeightFront < (ftoFHeight-.8)):
            frontFenestZCoordUpper = .75 +glazingHeightFront
            frontFenestZCoordLower = .75
        else:
            frontFenestZCoordUpper = ftoFHeight - .05
            frontFenestZCoordLower = ftoFHeight - .05 - glazingHeightFront
            if (frontFenestZCoordLower < .05):
                frontFenestZCoordLower = .05
        glazingHeightLeft = round((((ftoFHeight * width) *glazing_left) / 100) / (width-.1), 4)
        if (glazingHeightLeft < (ftoFHeight-.8)):
            leftFenestZCoordUpper = .75 +glazingHeightLeft
            leftFenestZCoordLower = .75
        else:
            leftFenestZCoordUpper = ftoFHeight - .05
            leftFenestZCoordLower = ftoFHeight - .05 - glazingHeightLeft
            if (leftFenestZCoordLower < .05):
                leftFenestZCoordLower = .05
        glazingHeightBack = round((((ftoFHeight * length) *glazing_back) / 100) / (length-.1), 4)
        if (glazingHeightBack < (ftoFHeight-.8)):
            backFenestZCoordUpper = .75 +glazingHeightBack
            backFenestZCoordLower = .75
        else:

            backFenestZCoordUpper = ftoFHeight - .05
            backFenestZCoordLower = ftoFHeight - .05 - glazingHeightBack
            if (backFenestZCoordLower < .05):
                backFenestZCoordLower = .05
        glazingHeightRight = round((((ftoFHeight * width) *glazing_right) / 100) / (width-.1), 4)
        if (glazingHeightRight < (ftoFHeight-.8)):
            rightFenestZCoordUpper = .75 +glazingHeightRight
            rightFenestZCoordLower = .75
        else:
            rightFenestZCoordUpper = ftoFHeight - .05
            rightFenestZCoordLower = ftoFHeight - .05 - glazingHeightRight
            if (rightFenestZCoordLower < .05):
                rightFenestZCoordLower = .05
        
        material_rad = """
    Material,
    Radiant Barrier,     !- Name
    Rough,                   !- Roughness
    0.012,                   !- Thickness {m}
    0.25,                    !- Conductivity {W/m-K}
    900,                     !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    0.2,                     !- Thermal Absorptance
    0.3,                     !- Solar Absorptance
    0.3;                     !- Visible Absorptance """
        material = "";
        if( layer1 == "F08 Metal surface" or layer2 == "F08 Metal surface" or layer3 == "F08 Metal surface" or layer4 == "F08 Metal surface" ):

            material = material + """
    Material,
    F08 Metal surface,       !- Name
    Smooth,                  !- Roughness
    0.0008,                  !- Thickness {m}
    45.28,                   !- Conductivity {W/m-K}
    7824,                    !- Density {kg/m3}
    500;                     !- Specific Heat {J/kg-K} """

        if( layer1 == "12mm Thick Mortar" or layer2 == "12mm Thick Mortar" or layer3 == "12mm Thick Mortar" or layer4 == "12mm Thick Mortar" ):

            material = material + """
    Material,
    12mm Thick Mortar,                  !- Name
    MediumSmooth,            !- Roughness
    0.012,                   !- Thickness {m}
    0.88,                    !- Conductivity {W/m-K}
    2800,                    !- Density {kg/m3}
    896,                     !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.6,                     !- Solar Absorptance
    0.6;                     !- Visible Absorptance """

        if( layer1 == "F13 Built-up roofing" or layer2 == "F13 Built-up roofing" or layer3 == "F13 Built-up roofing" or layer4 == "F13 Built-up roofing" ):

            material = material + """   
    Material,
    F13 Built-up roofing,    !- Name
    Rough,                   !- Roughness
    0.0095,                  !- Thickness {m}
    0.16,                    !- Conductivity {W/m-K}
    1120,                    !- Density {kg/m3}
    1460;                    !- Specific Heat {J/kg-K} """

        if( layer1 == "150mm Thick RCC Slab" or layer2 == "150mm Thick RCC Slab" or layer3 == "150mm Thick RCC Slab" or layer4 == "150mm Thick RCC Slab" ):

            material = material + """
    Material,
    150mm Thick RCC Slab,  !- Name
    MediumRough,             !- Roughness
    0.152,                   !- Thickness {m}
    2.5,                     !- Conductivity {W/m-K}
    2400,                    !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.6,                     !- Solar Absorptance
    0.6;                     !- Visible Absorptance """

        if( layer1 == "200mm Thick RCC Slab" or layer2 == "200mm Thick RCC Slab" or layer3 == "200mm Thick RCC Slab" or layer4 == "200mm Thick RCC Slab" ):

            material = material + """
    Material,
    200mm Thick RCC Slab,  !- Name
    MediumRough,             !- Roughness
    0.200,                   !- Thickness {m}
    2.5,                     !- Conductivity {W/m-K}
    2400,                    !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.6,                     !- Solar Absorptance
    0.6;                     !- Visible Absorptance """

        if( layer1 == "Gypsum Plasterboard" or layer2 == "Gypsum Plasterboard" or layer3 == "Gypsum Plasterboard" or layer4 == "Gypsum Plasterboard" ):

            material = material + """
    Material,
    Gypsum Plasterboard,     !- Name
    Rough,                   !- Roughness
    0.012,                   !- Thickness {m}
    0.25,                    !- Conductivity {W/m-K}
    900,                     !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.5,                     !- Solar Absorptance
    0.5;                     !- Visible Absorptance """
        if( layer1 == "F14 Slate or tile" or layer2 == "F14 Slate or tile" or layer3 == "F14 Slate or tile" or layer4 == "F14 Slate or tile" ):

            material = material + """
    Material,
    F14 Slate or tile,       !- Name
    Smooth,                  !- Roughness
    0.0127,                  !- Thickness {m}
    1.59,                    !- Conductivity {W/m-K}
    1920,                    !- Density {kg/m3}
    1260;                    !- Specific Heat {J/kg-K} """
        if( layer1 == "F05 Ceiling air space resistance" or layer2 == "F05 Ceiling air space resistance" or layer3 == "F05 Ceiling air space resistance" or layer4 == "F05 Ceiling air space resistance" ):

            material = material + """
    Material:AirGap,
    F05 Ceiling air space resistance,  !- Name
    0.18;                    !- Thermal Resistance {m2-K/W}
    0.6;                     !- Visible Absorptance """

        if( layer1 == "F16 Acoustic tile" or layer2 == "F16 Acoustic tile" or layer3 == "F16 Acoustic tile" or layer4 == "F16 Acoustic tile" ):

            material = material + """
    Material,
    F16 Acoustic tile,       !- Name
    MediumSmooth,            !- Roughness
    0.0191,                  !- Thickness {m}
    0.06,                    !- Conductivity {W/m-K}
    368,                     !- Density {kg/m3}
    590;                     !- Specific Heat {J/kg-K} """

        if( layer1 == "Insulation" or layer2 == "Insulation" or layer3 == "Insulation" or layer4 == "Insulation" ):

            material = material + """
    Material:NoMass,
    Insulation,              !- Name
    MediumRough,             !- Roughness
    0.033,                   !- Thermal Resistance {m2-K/W}
    0.9,                     !- Thermal Absorptance
    0.7,                     !- Solar Absorptance
    0.7;                     !- Visible Absorptance """
        baseMaterial = material
        proposedMaterial = material
        baseConstruction = """
    Construction,
    Roof,                    !- Name
    Roof Coating,            !- Outside Layer\n  """
        
        if (layer1 != "none"):
            baseConstruction = baseConstruction + layer1
        if (layer2 != "none"):
            baseConstruction = baseConstruction + ",\n" + layer2
        if (layer3 != "none"):
            baseConstruction = baseConstruction + ",\n" + layer3
        if (layer4 != "none"):
            baseConstruction = baseConstruction + ",\n" + layer4


        baseConstruction = baseConstruction + ";\n"
        proposedConstruction = """
    Construction,
    Roof,                    !- Name
    Roof Coating,            !- Outside Layer\n """
        
        if (layer1 != "none"):
            proposedConstruction = proposedConstruction + layer1
        if (layer2 != "none"):
            proposedConstruction = proposedConstruction + ",\n" + layer2
        if (layer3 != "none"):
            proposedConstruction = proposedConstruction + ",\n" + layer3
        if (layer4 != "none"):
            proposedConstruction = proposedConstruction + ",\n" + layer4

        if(Radiant_barrier == "ON"):
            proposedMaterial = proposedMaterial + material_rad
            proposedConstruction = proposedConstruction + ",\n    Radiant Barrier"
        
        proposedConstruction = proposedConstruction + ";\n"    

        

        
        static_dir =  settings.STATICFILES_DIRS[1] #os.path.join(BASE_DIR, 'static')
        try:
            folder = os.mkdir(os.path.join(static_dir,"model_idf",file_uuid))
            base_folder = os.mkdir(os.path.join(static_dir,"model_idf",file_uuid,"base"))
            proposed_folder = os.mkdir(os.path.join(static_dir,"model_idf",file_uuid,"proposed"))
            folder2 = os.mkdir(os.path.join(BASE_DIR,"templates","html_dir",file_uuid))
            base_html_folder = os.mkdir(os.path.join(BASE_DIR,"templates","html_dir",file_uuid,"base"))
            proposed_html_folder = os.mkdir(os.path.join(BASE_DIR,"templates","html_dir",file_uuid,"proposed"))
        except OSError as e:
            if e.errno != errno.EEXIST:
                # directory already exists
                pass
            else:
                print(e)
        scheduleClass = ""
        hvac_string = ""
        modelTemplate = ""

        if (Building_type == "office"):
            if (HVAC_details == "uc"):
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Office/Main_Office_UC.idf")
            else:
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Office/Office_Main.idf")
            if (HVAC_details == "ptac"):
                fname = os.path.join(BASE_DIR, 'static/idfsnippets/Office/Schedule_Office_PTHP.txt')
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Office/HVAC_Office_PTHP.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()
            elif (HVAC_details == "pszhp"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Office/Schedule_Office_Others_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Office/HVAC_Office_PSZHP_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "watercooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Office/Schedule_Office_Others_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Office/HVAC_Office_Watercooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()
            elif (HVAC_details == "aircooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Office/Schedule_Office_Others_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Office/HVAC_Office_Aircooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()
            elif (HVAC_details == "uc"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Office/Schedule_Office_UC.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Office/HVAC_Office_UC.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()
        elif (Building_type == "institutional"):    
            if (HVAC_details == "uc"):
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Institute/Main_Institute_UC.idf")
            else:
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Institute/Institute_Main.idf")
            if (HVAC_details == "ptac"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Institute/Schedule_Institute_Others_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Institute/HVAC_Institute_PTHP_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()
        
            elif (HVAC_details == "pszhp"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Institute/Schedule_Institute_Others_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Institute/HVAC_Institute_PSZHP_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "watercooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Institute/Schedule_Institute_Others_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Institute/HVAC_Institute_Watercooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "aircooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Institute/Schedule_Institute_Aircooled_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Institute/HVAC_Institute_Aircooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "uc"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Institute/Schedule_Institute_UC.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Institute/HVAC_Institute_UC.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()
        elif (Building_type == "retail"):
                
            if (HVAC_details == "uc"):
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Retail/Main_Retail_UC.idf")
            
            else:
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Retail/Retail_Main.idf")
            
            if (HVAC_details == "ptac"):

                fname = os.path.join(BASE_DIR,"static/idfsnippets/Retail/Schedule_Retail_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Retail/HVAC_Retail_PTHP_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "pszhp"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Retail/Schedule_Retail_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Retail/HVAC_Retail_PSZHP_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "watercooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Retail/Schedule_Retail_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Retail/HVAC_Retail_Watercooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "aircooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Retail/Schedule_Retail_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Retail/HVAC_Retail_Aircooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "uc"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Retail/Schedule_Retail_UC.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Retail/HVAC_Retail_UC.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

                
        elif (Building_type == "residentialallday"):
            if (HVAC_details == "uc"):
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/Main_Residential_24H_UC.idf")
            
            else:
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/Residential_24_Main.idf")
            
            if (HVAC_details == "ptac"):
            
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/Schedule_Residential_24_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/HVAC_Residential_24_PTHP_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "pszhp"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/Schedule_Residential_24_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/HVAC_Residential_24_PSZHP_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "watercooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/Schedule_Residential_24_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/HVAC_Residential_24_Watercooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "aircooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/Schedule_Residential_24_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/HVAC_Residential_24_Aircooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "uc"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/Schedule_Residential_24_UC.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/HVAC_Residential_24H_UC.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

                
        elif (Building_type == "residentialonlynight"):
                
            if (HVAC_details == "uc"):
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/Main_Residential_Night_UC.idf")
            
            else:
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/Residential_Night_Main.idf")
            
            if (HVAC_details == "ptac"):

                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/Schedule_Residential_Night_All.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/HVAC_Residential_Night_PTHP.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()
            
            elif (HVAC_details == "pszhp"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/Schedule_Residential_Night_All.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/HVAC_Residential_Night_PSZHP.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "watercooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/Schedule_Residential_Night_All.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/HVAC_Residential_Night_Watercooled.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "aircooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/Schedule_Residential_Night_All.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/HVAC_Residential_Night_Aircooled.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "uc"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/Schedule_Residential_Night_UC.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/HVAC_Residential_Night_UC.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()


        appendix_G = 0
        if (HVAC_details == "pszhp"):
            appendix_G = 5
        elif (HVAC_details == "ptac"):
            appendix_G = 3
        elif (HVAC_details == "watercooled" or HVAC_details == "aircooled"):
            appendix_G =9
        elif (HVAC_details == "uc"):
            appendix_G = 3                                   

        dNt =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        file1 = open(modelTemplate, "r") or sys.exit(
                    "can't open HVAC_details, scheduleClass, modelTemplate for reading")
        

        theData = file1.read()
        theData = theData.replace('%ScheduleString%',scheduleClass)
        theData = theData.replace('%NegativePerimPlusFenesPerim%',str(NegativePerimPlusFenesPerim))
        theData = theData.replace('%LengthMinusPerimitersBoth%',str(LengthMinusPerimitersBoth))
        theData = theData.replace('%PerimeterNeg%',str(perimeterLengthNegative))
        theData = theData.replace('%Perimeter%',str(perimeterLength))              
        theData = theData.replace('%building_desc%',building_desc)
        theData = theData.replace('%ThermalAbsorptance%',"0.9")
        theData = theData.replace('%SolarAbsorptance%',str(round(solarAbBase, 3)))
        theData = theData.replace('%VisibleAbsorptance%',str(round(visibleAbBase, 3)))
        theData = theData.replace('%FloorToFloorHeight%',str(ftoFHeight))
        theData = theData.replace('%LengthMinusPerimeterDouble%',str(round(width-9.14, 4)))
        theData = theData.replace('%LengthMinusNinePointOneFour%',str(round(length-9.14, 4)))
        theData = theData.replace('%Width%',str(round(width, 4)))
        theData = theData.replace('%LengthMinusPerimeter%',str(round(width-4.57, 4)))
        theData = theData.replace('%LengthMinusFourPointFiveSeven%',str(round(length-4.57, 4)))
        theData = theData.replace('%leftFenestZCoordLower%',str(round(leftFenestZCoordLower, 4)))
        theData = theData.replace('%frontFenestZCoordUpper%',str(round(frontFenestZCoordUpper, 4)))
        theData = theData.replace('%frontFenestZCoordLower%',str(round(frontFenestZCoordLower, 4)))
        theData = theData.replace('%LengthMinusPointZeroFive%',str(round(length-0.05, 4)))   
        theData = theData.replace('%rightFenestZCoordUpper%',str(round(rightFenestZCoordUpper, 4)))
        theData = theData.replace('%rightFenestZCoordLower%',str(round(rightFenestZCoordLower, 4)))
        theData = theData.replace('%WidthMinusPointZeroFive%',str(round(width-0.05, 4)))
        theData = theData.replace('%LengthMinusFourPointSixTwo%',str(round(length-4.62, 4)))
        theData = theData.replace('%backFenestZCoordUpper%',str(round(backFenestZCoordUpper, 4)))
        theData = theData.replace('%backFenestZCoordLower%',str(round(backFenestZCoordLower, 4)))
        theData = theData.replace('%leftFenestZCoordUpper%',str(round(leftFenestZCoordUpper, 4)))
        theData = theData.replace('%OriginZ1_x%',str(round(OriginZ1_x, 4)))
        theData = theData.replace('%OriginZ1_y%',str(round(OriginZ1_y, 4)))
        theData = theData.replace('%OriginZ1_z%',str(round(OriginZ1_z, 4)))
        theData = theData.replace('%OriginZ2_x%',str(round(OriginZ2_x, 4)))
        theData = theData.replace('%OriginZ2_y%',str(round(OriginZ2_y, 4)))
        theData = theData.replace('%OriginZ2_z%',str(round(OriginZ2_z, 4)))
        theData = theData.replace('%OriginZ3_x%',str(round(OriginZ3_x, 4)))
        theData = theData.replace('%OriginZ3_y%',str(round(OriginZ3_y, 4)))
        theData = theData.replace('%OriginZ3_z%',str(round(OriginZ3_z, 4)))
        theData = theData.replace('%OriginZ5_x%',str(round(OriginZ5_x, 4)))
        theData = theData.replace('%OriginZ5_y%',str(round(OriginZ5_y, 4)))
        theData = theData.replace('%OriginZ5_z%',str(round(OriginZ5_z, 4)))
        theData = theData.replace('%Volume%',str(round(volume, 4)))
        theData = theData.replace('%Length%',str(round(length, 4)))
        theData = theData.replace('%Width%',str(round(width, 4)))
        theData = theData.replace('%VolumeLength%',str(round(volumeLength, 4)))
        theData = theData.replace('%VolumeWidth%',str(round(volumeWidth, 4)))
        theData = theData.replace('%VolumeCenter%',str(round(volumeCenter, 4)))
        theData = theData.replace('%ThermalAbsorptance%',str(thermalAbBase))
        theData = theData.replace('%LPD%',str(Lighting_power))
        theData = theData.replace('%EPD%',str(Equipment_power))
        theData = theData.replace('%volumeLength%',str(volumeLength))
        theData = theData.replace('%date_n_time%',str(dNt))
        theData = theData.replace('%site_location%',str(Location))
        theData = theData.replace('%appendix_type%',str(appendix_G))
        theData = theData.replace('%SystemCOP%',str(System_cop))

        base_path = os.path.join(static_dir,"model_idf",file_uuid,"base","model.idf")
        
        
        with open(base_path,'w') as file2:

            file2.write(theData)
            file2.write(baseMaterial)
            file2.write(baseConstruction)
            file2.write(hvac_string)

        file2.close()
        file1.close()


        file1 = open(modelTemplate, "r") 
        theData = file1.read()


        theData = theData.replace('%ScheduleString%',scheduleClass)
        theData = theData.replace('%NegativePerimPlusFenesPerim%',str(NegativePerimPlusFenesPerim))
        theData = theData.replace('%LengthMinusPerimitersBoth%',str(LengthMinusPerimitersBoth))
        theData = theData.replace('%PerimeterNeg%',str(perimeterLengthNegative))
        theData = theData.replace('%Perimeter%',str(perimeterLength))              
        theData = theData.replace('%building_desc%',building_desc)
        theData = theData.replace('%ThermalAbsorptance%',"0.9")
        theData = theData.replace('%SolarAbsorptance%',str(round(solarAbProposed, 3)))
        theData = theData.replace('%VisibleAbsorptance%',str(round(visibleAbProposed, 3)))
        theData = theData.replace('%FloorToFloorHeight%',str(ftoFHeight))
        theData = theData.replace('%LengthMinusPerimeterDouble%',str(round(width-9.14, 4)))
        theData = theData.replace('%LengthMinusNinePointOneFour%',str(round(length-9.14, 4)))
        theData = theData.replace('%Width%',str(round(width, 4)))
        theData = theData.replace('%LengthMinusPerimeter%',str(round(width-4.57, 4)))
        theData = theData.replace('%LengthMinusFourPointFiveSeven%',str(round(length-4.57, 4)))
        theData = theData.replace('%leftFenestZCoordLower%',str(round(leftFenestZCoordLower, 4)))
        theData = theData.replace('%frontFenestZCoordUpper%',str(round(frontFenestZCoordUpper, 4)))
        theData = theData.replace('%frontFenestZCoordLower%',str(round(frontFenestZCoordLower, 4)))
        theData = theData.replace('%LengthMinusPointZeroFive%',str(round(length-0.05, 4)))
        theData = theData.replace('%rightFenestZCoordUpper%',str(round(rightFenestZCoordUpper, 4)))
        theData = theData.replace('%rightFenestZCoordLower%',str(round(rightFenestZCoordLower, 4)))
        theData = theData.replace('%WidthMinusPointZeroFive%',str(round(width-0.05, 4)))
        theData = theData.replace('%LengthMinusFourPointSixTwo%',str(round(length-4.62, 4)))
        theData = theData.replace('%backFenestZCoordUpper%',str(round(backFenestZCoordUpper, 4)))
        theData = theData.replace('%backFenestZCoordLower%',str(round(backFenestZCoordLower, 4)))
        theData = theData.replace('%leftFenestZCoordUpper%',str(round(leftFenestZCoordUpper, 4)))
        theData = theData.replace('%OriginZ1_x%',str(round(OriginZ1_x, 4)))
        theData = theData.replace('%OriginZ1_y%',str(round(OriginZ1_y, 4)))
        theData = theData.replace('%OriginZ1_z%',str(round(OriginZ1_z, 4)))
        theData = theData.replace('%OriginZ2_x%',str(round(OriginZ2_x, 4)))
        theData = theData.replace('%OriginZ2_y%',str(round(OriginZ2_y, 4)))
        theData = theData.replace('%OriginZ2_z%',str(round(OriginZ2_z, 4)))
        theData = theData.replace('%OriginZ3_x%',str(round(OriginZ3_x, 4)))
        theData = theData.replace('%OriginZ3_y%',str(round(OriginZ3_y, 4)))
        theData = theData.replace('%OriginZ3_z%',str(round(OriginZ3_z, 4)))
        theData = theData.replace('%OriginZ5_x%',str(round(OriginZ5_x, 4)))
        theData = theData.replace('%OriginZ5_y%',str(round(OriginZ5_y, 4)))
        theData = theData.replace('%OriginZ5_z%',str(round(OriginZ5_z, 4)))
        theData = theData.replace('%Volume%',str(round(volume, 4)))
        theData = theData.replace('%Length%',str(round(length, 4)))
        theData = theData.replace('%Width%',str(round(width, 4)))
        theData = theData.replace('%VolumeLength%',str(round(volumeLength, 4)))
        theData = theData.replace('%VolumeWidth%',str(round(volumeWidth, 4)))
        theData = theData.replace('%VolumeCenter%',str(round(volumeCenter, 4)))
        theData = theData.replace('%ThermalAbsorptance%',str(thermalAbProposed))
        theData = theData.replace('%LPD%',str(Lighting_power))
        theData = theData.replace('%EPD%',str(Equipment_power))
        theData = theData.replace('%volumeLength%',str(volumeLength))
        theData = theData.replace('%date_n_time%',str(dNt))
        theData = theData.replace('%site_location%',str(Location))
        theData = theData.replace('%appendix_type%',str(appendix_G))
        theData = theData.replace('%SystemCOP%',str(System_cop))
        proposed_path = os.path.join(static_dir,"model_idf",file_uuid,"proposed","model.idf")
        with open(proposed_path,'w') as file2:
            file2.write(theData)
            file2.write(baseMaterial)
            file2.write(baseConstruction)
            file2.write(hvac_string)
        file2.close()
        file1.close()
        input_dict = {"Location":str(Location), "Building_type":str(Building_type), "Roof_area":str(Roof_area), "Layer_1":str(layer1),
            "Layer_2":str(layer2),"Layer_3":str(layer3),"Layer_4":str(layer4),"Radiant_barrier":str(Radiant_barrier),"Reflectivity_base":str(Reflectivity_base),"Emissivity_base":str(Emissivity_base),
            "Cost_base":str(Cost_base),"Life_base":str(Life_base),"Reflectivity_proposed":str(Reflectivity_proposed),"Emissivity_proposed":str(Emissivity_proposed),"Cost_proposed":str(Cost_proposed),
            "Life_proposed":str(Life_proposed),"System_cop":str(System_cop), "HVAC_details":str(HVAC_details),"Lighting_power":str(Lighting_power),"Equipment_power":str(Equipment_power),"win_area_north":str(win_area_north),
            "win_area_south":str(win_area_south),"win_area_east":str(win_area_east),"win_area_west":str(win_area_west),"Electricity":str(Electricity),"emailid":str(emailid)}
        print(json.dumps(input_dict))
        form_detailed_data = Detailed_Data.objects.filter(**input_dict).first()
        if form_detailed_data:
           return redirect('display_results/'+str(form_detailed_data.id)+"/")
        else:
            input_dict['file_uuid'] = file_uuid
            input_dict['username'] = user_name
            form_detailed_data = Detailed_Data.objects.create(**input_dict)
            print("New entry created.")
        celery_task = run_simulation.delay(form_detailed_data.pk) 
        form_detailed_data.task_id = celery_task.id
        form_detailed_data.save()
        print('done')
        print(celery_task.id)
        result = AsyncResult(celery_task.id)
        print(f'Current Status: {result.status}')
        print(celery_task.ready())
        pk = form_detailed_data.id
        return postdata_loader(request, pk)
    except Exception as e:
        print(f"Error occurred: {e}")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error details: {exc_type}, {fname}, {exc_tb.tb_lineno}")
        
        # Return a generic error message and try to reload the form data if needed
        #pk = form_detailed_data.pk if 'form_detailed_data' in locals() and form_detailed_data else None
        return postdata_loader(request, None)
def parametric(request):
    pk = None    
    msg = ""
    try:
        # GENERATES UNIQUE CODE FOR WORKING DIRECTORY OF USER FOR A PARTICULAR SIMULATION
        file_uuid = str(uuid.uuid1())
        Location = request.POST["Location"]
        Building_type = request.POST["Building_type"]
        # Roof_area = request.POST["Roof_area"]
        Roof_area = request.POST.get("Roof_area","130")
        
        layer1 = request.POST["layer1"]
        layer2 = request.POST["layer2"]
        layer3 = request.POST["layer3"]
        layer4 = request.POST["layer4"]

        Radiant_barrier = request.POST["Radiant_barrier"]

        Reflectivity_base = request.POST["reflectivity_base"]
        Emissivity_base = request.POST["emissivity_base"]
        Cost_base = request.POST["cost_base"]
        Life_base = request.POST["life_base"]

        Reflectivity_proposed = request.POST["reflectivity_proposed"]
        Emissivity_proposed = request.POST["emissivity_proposed"]
        Cost_proposed = request.POST["cost_proposed"]
        Life_proposed = request.POST["life_proposed"]

        HVAC_details = request.POST["HVAC_details"]
        System_cop = request.POST["system_cop"]
        Lighting_power = request.POST["lighting_power"]
        Equipment_power = request.POST["equipment_power"]
        win_area_north = request.POST["win_area_north"]
        win_area_south = request.POST["win_area_south"]
        win_area_east = request.POST["win_area_east"]
        win_area_west = request.POST["win_area_west"]
        
        Electricity = request.POST["Electricity"]
        emailid = request.POST["emailid2"]
        user_name = request.POST["user_name"]
        kvalue = request.POST["kvalue"]


        if (Electricity == ""):
            Electricity = 6
        building_desc = "Coolroof_IDF"
        if (Roof_area == ""):
            Roof_area = 130
        if (Reflectivity_base == ""):
            Reflectivity_base = 0.3
        if(Emissivity_base == ""):
            Emissivity_base = 0.9
        if(Cost_base == ""):
            Cost_base = 200
        if (Life_base == ""):
            Life_base = 10
        if (Reflectivity_proposed == ""):
            Reflectivity_proposed = 0.7
        if (Emissivity_proposed == ""):
            Emissivity_proposed = 0.9
        if (Cost_proposed == ""):
            Cost_proposed = 500
        if (Life_proposed == ""):
            Life_proposed = 5
        if (System_cop == ""):
            System_cop = 3
        if (Lighting_power == ""):
            Lighting_power = 10.8
        if (Equipment_power == ""):
            Equipment_power = 16.5
        if (win_area_north == ""):
            win_area_north = 11.97
        if (win_area_south == ""):
            win_area_south = 11.97
        if(win_area_east == ""):
            win_area_east = 11.97
        if (win_area_west == ""):
            win_area_west = 11.97
        

        # minthickness=0.1
        # maxthickness=250.1
        # thicknessinterval=25
        # sim_count=0
        # for(x=minthickness;x<=maxthickness;x=x+thicknessinterval)
        #     sim_count=sim_count+1
        # maxsim_count=sim_count
        # sim_count=0
        # for(x=minthickness;x<=maxthickness;x=x+thicknessinterval)
        #     sim_count=sim_count+1
        #     current_thickness=x
        
        # r_val_para=current_thickness/k_insulationvalue
        # if(r_val_para==0)
        #     r_val_para=0.1
        # r_val_para=r_val_para/1000
        
        
        weather_file = os.path.join(BASE_DIR,"static/WeatherData/")+Location+".epw" 
                                                                                                                                

        length = width = math.sqrt(int(Roof_area))
        
        solarAbBase = visibleAbBase = 1 - float(Reflectivity_base)
        solarAbProposed = visibleAbProposed = 1 - float(Reflectivity_proposed)
        thermalAbBase = float(Emissivity_base)
        thermalAbProposed = float(Emissivity_proposed)
        OriginZ1_x = 0
        OriginZ1_y = 0
        OriginZ1_z = 0  
        OriginZ2_x = float(length)
        OriginZ2_y = 0
        OriginZ2_z = 0
        OriginZ3_x = 4.57
        OriginZ3_y = float(width) - 4.57
        OriginZ3_z = 0
        OriginZ5_x = 4.57
        OriginZ5_y = 4.57
        OriginZ5_z = 0
        ftoFHeight = 3.5
        glazing_front = float(win_area_north)
        glazing_back = float(win_area_south)
        glazing_left = float(win_area_west)
        glazing_right = float(win_area_east)
        volume = ftoFHeight * float(Roof_area)
        
        
        volumeLength = round(ftoFHeight * 4.57 * (length-4.57), 4)
        volumeWidth = round(ftoFHeight * 4.57 * (width-4.57), 4)
        volumeCenter = round(ftoFHeight * (length-9.14) * (width-9.14), 4)
        perimeterLength = 4.5700
        perimeterLengthNegative = -4.5700
        LengthMinusPerimitersBoth = length - 4.57 - .05
        NegativePerimPlusFenesPerim = -4.57 + .05
        glazingHeightFront = round((((ftoFHeight * length) *glazing_front) / 100) / (length-.1), 4)
        
        if (glazingHeightFront < (ftoFHeight-.8)):
            frontFenestZCoordUpper = .75 +glazingHeightFront
            frontFenestZCoordLower = .75
        else:
            frontFenestZCoordUpper = ftoFHeight - .05
            frontFenestZCoordLower = ftoFHeight - .05 - glazingHeightFront
            if (frontFenestZCoordLower < .05):
                frontFenestZCoordLower = .05
        glazingHeightLeft = round((((ftoFHeight * width) *glazing_left) / 100) / (width-.1), 4)
        if (glazingHeightLeft < (ftoFHeight-.8)):
            leftFenestZCoordUpper = .75 +glazingHeightLeft
            leftFenestZCoordLower = .75
        else:
            leftFenestZCoordUpper = ftoFHeight - .05
            leftFenestZCoordLower = ftoFHeight - .05 - glazingHeightLeft
            if (leftFenestZCoordLower < .05):
                leftFenestZCoordLower = .05
        glazingHeightBack = round((((ftoFHeight * length) *glazing_back) / 100) / (length-.1), 4)
        if (glazingHeightBack < (ftoFHeight-.8)):
            backFenestZCoordUpper = .75 +glazingHeightBack
            backFenestZCoordLower = .75
        else:

            backFenestZCoordUpper = ftoFHeight - .05
            backFenestZCoordLower = ftoFHeight - .05 - glazingHeightBack
            if (backFenestZCoordLower < .05):
                backFenestZCoordLower = .05
        glazingHeightRight = round((((ftoFHeight * width) *glazing_right) / 100) / (width-.1), 4)
        if (glazingHeightRight < (ftoFHeight-.8)):
            rightFenestZCoordUpper = .75 +glazingHeightRight
            rightFenestZCoordLower = .75
        else:
            rightFenestZCoordUpper = ftoFHeight - .05
            rightFenestZCoordLower = ftoFHeight - .05 - glazingHeightRight
            if (rightFenestZCoordLower < .05):
                rightFenestZCoordLower = .05
        
        material_rad = """
    Material,
    Radiant Barrier,     !- Name
    Rough,                   !- Roughness
    0.012,                   !- Thickness {m}
    0.25,                    !- Conductivity {W/m-K}
    900,                     !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    0.2,                     !- Thermal Absorptance
    0.3,                     !- Solar Absorptance
    0.3;                     !- Visible Absorptance """
        material = "";
        if( layer1 == "F08 Metal surface" or layer2 == "F08 Metal surface" or layer3 == "F08 Metal surface" or layer4 == "F08 Metal surface" ):

            material = material + """
    Material,
    F08 Metal surface,       !- Name
    Smooth,                  !- Roughness
    0.0008,                  !- Thickness {m}
    45.28,                   !- Conductivity {W/m-K}
    7824,                    !- Density {kg/m3}
    500;                     !- Specific Heat {J/kg-K} """

        if( layer1 == "12mm Thick Mortar" or layer2 == "12mm Thick Mortar" or layer3 == "12mm Thick Mortar" or layer4 == "12mm Thick Mortar" ):

            material = material + """
    Material,
    12mm Thick Mortar,                  !- Name
    MediumSmooth,            !- Roughness
    0.012,                   !- Thickness {m}
    0.88,                    !- Conductivity {W/m-K}
    2800,                    !- Density {kg/m3}
    896,                     !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.6,                     !- Solar Absorptance
    0.6;                     !- Visible Absorptance """

        if( layer1 == "F13 Built-up roofing" or layer2 == "F13 Built-up roofing" or layer3 == "F13 Built-up roofing" or layer4 == "F13 Built-up roofing" ):

            material = material + """   
    Material,
    F13 Built-up roofing,    !- Name
    Rough,                   !- Roughness
    0.0095,                  !- Thickness {m}
    0.16,                    !- Conductivity {W/m-K}
    1120,                    !- Density {kg/m3}
    1460;                    !- Specific Heat {J/kg-K} """

        if( layer1 == "150mm Thick RCC Slab" or layer2 == "150mm Thick RCC Slab" or layer3 == "150mm Thick RCC Slab" or layer4 == "150mm Thick RCC Slab" ):

            material = material + """
    Material,
    150mm Thick RCC Slab,  !- Name
    MediumRough,             !- Roughness
    0.152,                   !- Thickness {m}
    2.5,                     !- Conductivity {W/m-K}
    2400,                    !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.6,                     !- Solar Absorptance
    0.6;                     !- Visible Absorptance """

        if( layer1 == "200mm Thick RCC Slab" or layer2 == "200mm Thick RCC Slab" or layer3 == "200mm Thick RCC Slab" or layer4 == "200mm Thick RCC Slab" ):

            material = material + """
    Material,
    200mm Thick RCC Slab,  !- Name
    MediumRough,             !- Roughness
    0.200,                   !- Thickness {m}
    2.5,                     !- Conductivity {W/m-K}
    2400,                    !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.6,                     !- Solar Absorptance
    0.6;                     !- Visible Absorptance """

        if( layer1 == "Gypsum Plasterboard" or layer2 == "Gypsum Plasterboard" or layer3 == "Gypsum Plasterboard" or layer4 == "Gypsum Plasterboard" ):

            material = material + """
    Material,
    Gypsum Plasterboard,     !- Name
    Rough,                   !- Roughness
    0.012,                   !- Thickness {m}
    0.25,                    !- Conductivity {W/m-K}
    900,                     !- Density {kg/m3}
    1000,                    !- Specific Heat {J/kg-K}
    0.9,                     !- Thermal Absorptance
    0.5,                     !- Solar Absorptance
    0.5;                     !- Visible Absorptance """
        if( layer1 == "F14 Slate or tile" or layer2 == "F14 Slate or tile" or layer3 == "F14 Slate or tile" or layer4 == "F14 Slate or tile" ):

            material = material + """
    Material,
    F14 Slate or tile,       !- Name
    Smooth,                  !- Roughness
    0.0127,                  !- Thickness {m}
    1.59,                    !- Conductivity {W/m-K}
    1920,                    !- Density {kg/m3}
    1260;                    !- Specific Heat {J/kg-K} """
        if( layer1 == "F05 Ceiling air space resistance" or layer2 == "F05 Ceiling air space resistance" or layer3 == "F05 Ceiling air space resistance" or layer4 == "F05 Ceiling air space resistance" ):

            material = material + """
    Material:AirGap,
    F05 Ceiling air space resistance,  !- Name
    0.033;                    !- Thermal Resistance {m2-K/W}
    0.6;                     !- Visible Absorptance """

        if( layer1 == "F16 Acoustic tile" or layer2 == "F16 Acoustic tile" or layer3 == "F16 Acoustic tile" or layer4 == "F16 Acoustic tile" ):

            material = material + """
    Material,
    F16 Acoustic tile,       !- Name
    MediumSmooth,            !- Roughness
    0.0191,                  !- Thickness {m}
    0.06,                    !- Conductivity {W/m-K}
    368,                     !- Density {kg/m3}
    590;                     !- Specific Heat {J/kg-K} """

        if( layer1 == "Insulation" or layer2 == "Insulation" or layer3 == "Insulation" or layer4 == "Insulation" ):

            material = material + """
    Material:NoMass,
    Insulation,              !- Name
    MediumRough,             !- Roughness
    0.033,                   !- Thermal Resistance {m2-K/W}
    0.9,                     !- Thermal Absorptance
    0.7,                     !- Solar Absorptance
    0.7;                     !- Visible Absorptance """
            
        
        baseMaterial = material
        proposedMaterial = material
        baseConstruction = """
    Construction,
    Roof,                    !- Name
    Roof Coating,            !- Outside Layer\n  """
        
        if (layer1 != "none"):
            baseConstruction = baseConstruction + layer1
        if (layer2 != "none"):
            baseConstruction = baseConstruction + ",\n" + layer2
        if (layer3 != "none"):
            baseConstruction = baseConstruction + ",\n" + layer3
        if (layer4 != "none"):
            baseConstruction = baseConstruction + ",\n" + layer4


        baseConstruction = baseConstruction + ";\n"
        proposedConstruction = """
    Construction,
    Roof,                    !- Name
    Roof Coating,            !- Outside Layer\n """
        
        if (layer1 != "none"):
            proposedConstruction = proposedConstruction + layer1
        if (layer2 != "none"):
            proposedConstruction = proposedConstruction + ",\n" + layer2
        if (layer3 != "none"):
            proposedConstruction = proposedConstruction + ",\n" + layer3
        if (layer4 != "none"):
            proposedConstruction = proposedConstruction + ",\n" + layer4

        if(Radiant_barrier == "ON"):
            proposedMaterial = proposedMaterial + material_rad
            proposedConstruction = proposedConstruction + ",\n    Radiant Barrier"
        
        proposedConstruction = proposedConstruction + ";\n"    

        

        
        static_dir = settings.STATICFILES_DIRS[1] #os.path.join(BASE_DIR, 'static')
        try:
            folder = os.mkdir(os.path.join(static_dir,"model_idf",file_uuid))
            base_folder = os.mkdir(os.path.join(static_dir,"model_idf",file_uuid,"base"))
            proposed_folder = os.mkdir(os.path.join(static_dir,"model_idf",file_uuid,"proposed"))
            folder2 = os.mkdir(os.path.join(BASE_DIR,"templates","html_dir",file_uuid))
            base_html_folder = os.mkdir(os.path.join(BASE_DIR,"templates","html_dir",file_uuid,"base"))
            proposed_html_folder = os.mkdir(os.path.join(BASE_DIR,"templates","html_dir",file_uuid,"proposed"))

        except OSError as e:
            if e.errno != errno.EEXIST:
                # directory already exists
                pass
            else:
                print(e)

        scheduleClass = ""
        hvac_string = ""
        modelTemplate = ""

        if (Building_type == "office"):
            if (HVAC_details == "uc"):
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Office/Main_Office_UC.idf")
                
            
            else:
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Office/Office_Main.idf")
                

            if (HVAC_details == "ptac"):
                
                
                fname = os.path.join(BASE_DIR, 'static/idfsnippets/Office/Schedule_Office_PTHP.txt')

                fptr = open(fname, "r") or exit("Unable to open file!")
                
                scheduleClass = fptr.read()
                

                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Office/HVAC_Office_PTHP.txt")
                
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                
                file1.close()
                

            elif (HVAC_details == "pszhp"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Office/Schedule_Office_Others_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Office/HVAC_Office_PSZHP_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "watercooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Office/Schedule_Office_Others_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Office/HVAC_Office_Watercooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "aircooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Office/Schedule_Office_Others_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Office/HVAC_Office_Aircooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "uc"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Office/Schedule_Office_UC.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Office/HVAC_Office_UC.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

        elif (Building_type == "institutional"):

    
            if (HVAC_details == "uc"):
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Institute/Main_Institute_UC.idf")
        
            else:
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Institute/Institute_Main.idf")
        
            if (HVAC_details == "ptac"):
        
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Institute/Schedule_Institute_Others_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Institute/HVAC_Institute_PTHP_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()
        
            elif (HVAC_details == "pszhp"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Institute/Schedule_Institute_Others_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Institute/HVAC_Institute_PSZHP_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "watercooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Institute/Schedule_Institute_Others_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Institute/HVAC_Institute_Watercooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "aircooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Institute/Schedule_Institute_Aircooled_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Institute/HVAC_Institute_Aircooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "uc"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Institute/Schedule_Institute_UC.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Institute/HVAC_Institute_UC.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()
        elif (Building_type == "retail"):
                
            if (HVAC_details == "uc"):
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Retail/Main_Retail_UC.idf")
            
            else:
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Retail/Retail_Main.idf")
            
            if (HVAC_details == "ptac"):

                fname = os.path.join(BASE_DIR,"static/idfsnippets/Retail/Schedule_Retail_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Retail/HVAC_Retail_PTHP_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "pszhp"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Retail/Schedule_Retail_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Retail/HVAC_Retail_PSZHP_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "watercooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Retail/Schedule_Retail_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Retail/HVAC_Retail_Watercooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "aircooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Retail/Schedule_Retail_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Retail/HVAC_Retail_Aircooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "uc"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Retail/Schedule_Retail_UC.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Retail/HVAC_Retail_UC.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

                
        elif (Building_type == "residentialallday"):
            if (HVAC_details == "uc"):
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/Main_Residential_24H_UC.idf")
            
            else:
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/Residential_24_Main.idf")
            
            if (HVAC_details == "ptac"):
            
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/Schedule_Residential_24_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/HVAC_Residential_24_PTHP_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "pszhp"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/Schedule_Residential_24_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/HVAC_Residential_24_PSZHP_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "watercooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/Schedule_Residential_24_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/HVAC_Residential_24_Watercooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "aircooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/Schedule_Residential_24_All_back.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/HVAC_Residential_24_Aircooled_back.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "uc"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/Schedule_Residential_24_UC.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/24H/HVAC_Residential_24H_UC.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

                
        elif (Building_type == "residentialonlynight"):
                
            if (HVAC_details == "uc"):
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/Main_Residential_Night_UC.idf")
            
            else:
                modelTemplate = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/Residential_Night_Main.idf")
            
            if (HVAC_details == "ptac"):

                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/Schedule_Residential_Night_All.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/HVAC_Residential_Night_PTHP.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()
            
            elif (HVAC_details == "pszhp"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/Schedule_Residential_Night_All.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/HVAC_Residential_Night_PSZHP.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "watercooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/Schedule_Residential_Night_All.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/HVAC_Residential_Night_Watercooled.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "aircooled"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/Schedule_Residential_Night_All.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/HVAC_Residential_Night_Aircooled.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()

            elif (HVAC_details == "uc"):
                fname = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/Schedule_Residential_Night_UC.txt")
                fptr = open(fname, "r") or exit("Unable to open file!")
                scheduleClass = fptr.read()
                fptr.close()
                hvac_file = os.path.join(BASE_DIR,"static/idfsnippets/Residential/NightTime/HVAC_Residential_Night_UC.txt")
                file1 = open(hvac_file, "r") or sys.exit("can't open model template for reading")
                hvac_string = file1.read()
                file1.close()


        appendix_G = 0
        if (HVAC_details == "pszhp"):
            appendix_G = 5
        elif (HVAC_details == "ptac"):
            appendix_G = 3
        elif (HVAC_details == "watercooled" or HVAC_details == "aircooled"):
            appendix_G =9
        elif (HVAC_details == "uc"):
            appendix_G = 3                                   

        dNt =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        file1 = open(modelTemplate, "r") or sys.exit(
                    "can't open HVAC_details, scheduleClass, modelTemplate for reading")    

        theData = file1.read()
        theData = theData.replace('%ScheduleString%',scheduleClass)
        theData = theData.replace('%NegativePerimPlusFenesPerim%',str(NegativePerimPlusFenesPerim))
        theData = theData.replace('%LengthMinusPerimitersBoth%',str(LengthMinusPerimitersBoth))
        theData = theData.replace('%PerimeterNeg%',str(perimeterLengthNegative))
        theData = theData.replace('%Perimeter%',str(perimeterLength))              
        theData = theData.replace('%building_desc%',building_desc)
        theData = theData.replace('%ThermalAbsorptance%',"0.9")
        theData = theData.replace('%SolarAbsorptance%',str(round(solarAbBase, 3)))
        theData = theData.replace('%VisibleAbsorptance%',str(round(visibleAbBase, 3)))
        theData = theData.replace('%FloorToFloorHeight%',str(ftoFHeight))
        theData = theData.replace('%LengthMinusPerimeterDouble%',str(round(width-9.14, 4)))
        theData = theData.replace('%LengthMinusNinePointOneFour%',str(round(length-9.14, 4)))
        theData = theData.replace('%Width%',str(round(width, 4)))
        theData = theData.replace('%LengthMinusPerimeter%',str(round(width-4.57, 4)))
        theData = theData.replace('%LengthMinusFourPointFiveSeven%',str(round(length-4.57, 4)))
        theData = theData.replace('%leftFenestZCoordLower%',str(round(leftFenestZCoordLower, 4)))
        theData = theData.replace('%frontFenestZCoordUpper%',str(round(frontFenestZCoordUpper, 4)))
        theData = theData.replace('%frontFenestZCoordLower%',str(round(frontFenestZCoordLower, 4)))
        theData = theData.replace('%LengthMinusPointZeroFive%',str(round(length-0.05, 4)))   
        theData = theData.replace('%rightFenestZCoordUpper%',str(round(rightFenestZCoordUpper, 4)))
        theData = theData.replace('%rightFenestZCoordLower%',str(round(rightFenestZCoordLower, 4)))
        theData = theData.replace('%WidthMinusPointZeroFive%',str(round(width-0.05, 4)))
        theData = theData.replace('%LengthMinusFourPointSixTwo%',str(round(length-4.62, 4)))
        theData = theData.replace('%backFenestZCoordUpper%',str(round(backFenestZCoordUpper, 4)))
        theData = theData.replace('%backFenestZCoordLower%',str(round(backFenestZCoordLower, 4)))
        theData = theData.replace('%leftFenestZCoordUpper%',str(round(leftFenestZCoordUpper, 4)))
        theData = theData.replace('%OriginZ1_x%',str(round(OriginZ1_x, 4)))
        theData = theData.replace('%OriginZ1_y%',str(round(OriginZ1_y, 4)))
        theData = theData.replace('%OriginZ1_z%',str(round(OriginZ1_z, 4)))
        theData = theData.replace('%OriginZ2_x%',str(round(OriginZ2_x, 4)))
        theData = theData.replace('%OriginZ2_y%',str(round(OriginZ2_y, 4)))
        theData = theData.replace('%OriginZ2_z%',str(round(OriginZ2_z, 4)))
        theData = theData.replace('%OriginZ3_x%',str(round(OriginZ3_x, 4)))
        theData = theData.replace('%OriginZ3_y%',str(round(OriginZ3_y, 4)))
        theData = theData.replace('%OriginZ3_z%',str(round(OriginZ3_z, 4)))
        theData = theData.replace('%OriginZ5_x%',str(round(OriginZ5_x, 4)))
        theData = theData.replace('%OriginZ5_y%',str(round(OriginZ5_y, 4)))
        theData = theData.replace('%OriginZ5_z%',str(round(OriginZ5_z, 4)))
        theData = theData.replace('%Volume%',str(round(volume, 4)))
        theData = theData.replace('%Length%',str(round(length, 4)))
        theData = theData.replace('%Width%',str(round(width, 4)))
        theData = theData.replace('%VolumeLength%',str(round(volumeLength, 4)))
        theData = theData.replace('%VolumeWidth%',str(round(volumeWidth, 4)))
        theData = theData.replace('%VolumeCenter%',str(round(volumeCenter, 4)))
        theData = theData.replace('%ThermalAbsorptance%',str(thermalAbBase))
        theData = theData.replace('%LPD%',str(Lighting_power))
        theData = theData.replace('%EPD%',str(Equipment_power))
        theData = theData.replace('%volumeLength%',str(volumeLength))
        theData = theData.replace('%date_n_time%',str(dNt))
        theData = theData.replace('%site_location%',str(Location))
        theData = theData.replace('%appendix_type%',str(appendix_G))
        theData = theData.replace('%SystemCOP%',str(System_cop))

        base_path = os.path.join(static_dir,"model_idf",file_uuid,"base","model.idf")
        
        
        with open(base_path,'w') as file2:

            file2.write(theData)
            file2.write(baseMaterial)
            file2.write(baseConstruction)
            file2.write(hvac_string)

        file2.close()
        file1.close()


        file1 = open(modelTemplate, "r") 
        theData = file1.read()


        theData = theData.replace('%ScheduleString%',scheduleClass)
        theData = theData.replace('%NegativePerimPlusFenesPerim%',str(NegativePerimPlusFenesPerim))
        theData = theData.replace('%LengthMinusPerimitersBoth%',str(LengthMinusPerimitersBoth))
        theData = theData.replace('%PerimeterNeg%',str(perimeterLengthNegative))
        theData = theData.replace('%Perimeter%',str(perimeterLength))              
        theData = theData.replace('%building_desc%',building_desc)
        theData = theData.replace('%ThermalAbsorptance%',"0.9")
        theData = theData.replace('%SolarAbsorptance%',str(round(solarAbProposed, 3)))
        theData = theData.replace('%VisibleAbsorptance%',str(round(visibleAbProposed, 3)))
        theData = theData.replace('%FloorToFloorHeight%',str(ftoFHeight))
        theData = theData.replace('%LengthMinusPerimeterDouble%',str(round(width-9.14, 4)))
        theData = theData.replace('%LengthMinusNinePointOneFour%',str(round(length-9.14, 4)))
        theData = theData.replace('%Width%',str(round(width, 4)))
        theData = theData.replace('%LengthMinusPerimeter%',str(round(width-4.57, 4)))
        theData = theData.replace('%LengthMinusFourPointFiveSeven%',str(round(length-4.57, 4)))
        theData = theData.replace('%leftFenestZCoordLower%',str(round(leftFenestZCoordLower, 4)))
        theData = theData.replace('%frontFenestZCoordUpper%',str(round(frontFenestZCoordUpper, 4)))
        theData = theData.replace('%frontFenestZCoordLower%',str(round(frontFenestZCoordLower, 4)))
        theData = theData.replace('%LengthMinusPointZeroFive%',str(round(length-0.05, 4)))
        theData = theData.replace('%rightFenestZCoordUpper%',str(round(rightFenestZCoordUpper, 4)))
        theData = theData.replace('%rightFenestZCoordLower%',str(round(rightFenestZCoordLower, 4)))
        theData = theData.replace('%WidthMinusPointZeroFive%',str(round(width-0.05, 4)))
        theData = theData.replace('%LengthMinusFourPointSixTwo%',str(round(length-4.62, 4)))
        theData = theData.replace('%backFenestZCoordUpper%',str(round(backFenestZCoordUpper, 4)))
        theData = theData.replace('%backFenestZCoordLower%',str(round(backFenestZCoordLower, 4)))
        theData = theData.replace('%leftFenestZCoordUpper%',str(round(leftFenestZCoordUpper, 4)))
        theData = theData.replace('%OriginZ1_x%',str(round(OriginZ1_x, 4)))
        theData = theData.replace('%OriginZ1_y%',str(round(OriginZ1_y, 4)))
        theData = theData.replace('%OriginZ1_z%',str(round(OriginZ1_z, 4)))
        theData = theData.replace('%OriginZ2_x%',str(round(OriginZ2_x, 4)))
        theData = theData.replace('%OriginZ2_y%',str(round(OriginZ2_y, 4)))
        theData = theData.replace('%OriginZ2_z%',str(round(OriginZ2_z, 4)))
        theData = theData.replace('%OriginZ3_x%',str(round(OriginZ3_x, 4)))
        theData = theData.replace('%OriginZ3_y%',str(round(OriginZ3_y, 4)))
        theData = theData.replace('%OriginZ3_z%',str(round(OriginZ3_z, 4)))
        theData = theData.replace('%OriginZ5_x%',str(round(OriginZ5_x, 4)))
        theData = theData.replace('%OriginZ5_y%',str(round(OriginZ5_y, 4)))
        theData = theData.replace('%OriginZ5_z%',str(round(OriginZ5_z, 4)))
        theData = theData.replace('%Volume%',str(round(volume, 4)))
        theData = theData.replace('%Length%',str(round(length, 4)))
        theData = theData.replace('%Width%',str(round(width, 4)))
        theData = theData.replace('%VolumeLength%',str(round(volumeLength, 4)))
        theData = theData.replace('%VolumeWidth%',str(round(volumeWidth, 4)))
        theData = theData.replace('%VolumeCenter%',str(round(volumeCenter, 4)))
        theData = theData.replace('%ThermalAbsorptance%',str(thermalAbProposed))
        theData = theData.replace('%LPD%',str(Lighting_power))
        theData = theData.replace('%EPD%',str(Equipment_power))
        theData = theData.replace('%volumeLength%',str(volumeLength))
        theData = theData.replace('%date_n_time%',str(dNt))
        theData = theData.replace('%site_location%',str(Location))
        theData = theData.replace('%appendix_type%',str(appendix_G))
        theData = theData.replace('%SystemCOP%',str(System_cop))

        proposed_path = os.path.join(static_dir,"model_idf",file_uuid,"proposed","model.idf")
        
        
        with open(proposed_path,'w') as file2:

            file2.write(theData)
            file2.write(baseMaterial)
            file2.write(baseConstruction)
            file2.write(hvac_string)

        file2.close()
        file1.close()

        input_dict = {"Location":str(Location), "Building_type":str(Building_type), "Roof_area":str(Roof_area), "Layer_1":str(layer1),
            "Layer_2":str(layer2),"Layer_3":str(layer3),"Layer_4":str(layer4),"Radiant_barrier":str(Radiant_barrier),"Reflectivity_base":str(Reflectivity_base),"Emissivity_base":str(Emissivity_base),
            "Cost_base":str(Cost_base),"Life_base":str(Life_base),"Reflectivity_proposed":str(Reflectivity_proposed),"Emissivity_proposed":str(Emissivity_proposed),"Cost_proposed":str(Cost_proposed),
            "Life_proposed":str(Life_proposed),"System_cop":str(System_cop), "HVAC_details":str(HVAC_details),"Lighting_power":str(Lighting_power),"Equipment_power":str(Equipment_power),"win_area_north":str(win_area_north),
            "win_area_south":str(win_area_south),"win_area_east":str(win_area_east),"win_area_west":str(win_area_west),"Electricity":str(Electricity),"kvalue":str(kvalue),"emailid":str(emailid)}
        print(json.dumps(input_dict))
        form_detailed_data = Parametric_Data.objects.filter(**input_dict).first()
        if form_detailed_data:
           return redirect('display_results_parametric/'+str(form_detailed_data.id)+"/")
        else:
            input_dict['file_uuid'] = file_uuid
            input_dict['username'] = user_name
            form_detailed_data = Parametric_Data.objects.create(**input_dict)
            print("New entry created.")
        celery_task = run_simulation_parametric.delay(form_detailed_data.pk) 
        form_detailed_data.task_id = celery_task.id
        form_detailed_data.save()
        print('done')
        print(celery_task.id)
        result = AsyncResult(celery_task.id)
        print(f'Current Status: {result.status}')
        print(celery_task.ready())
        pk = form_detailed_data.id
        return postdata_loader_parametric(request, pk)
    except Exception as e:
        print(f"Error occurred: {e}")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error details: {exc_type}, {fname}, {exc_tb.tb_lineno}")
        # Return a generic error message and try to reload the form data if needed
        #pk = form_detailed_data.pk if 'form_detailed_data' in locals() and form_detailed_data else None
        return postdata_loader_parametric(request, None)
        
#############################################################################################################################

############################ SIMPLE ########################################
def getCompletionStatusSimple(request, pk):
    try: 
        form_detailed_data = Simple.objects.get(pk = pk)
    except Simple.DoesNotExist:
        return HttpResponse('Error in Simulation. Contact SysAdmin')
        # raise Exception('invalid pk')
    task_id = form_detailed_data.task_id
    result = AsyncResult(task_id)
    status = result.status
    form_detailed_data.result_status = status
    form_detailed_data.save()
    
    if result.ready():
        return HttpResponse('true')
    else:
        return  HttpResponse('false') 
def redirectResultsSimple(request, pk):
    try: 
        form_detailed_data = Simple.objects.get(pk=pk)
    except Simple.DoesNotExist:
        return HttpResponse('Error in Simulation. Contact SysAdmin')
    
    output = {}

    # Extract field values
    for field in form_detailed_data._meta.get_fields():
        output[field.name] = getattr(form_detailed_data, field.name)

    # Helper function to safely load JSON fields
    def safe_json_loads(value):
        try:
            return json.loads(value) if value and value.strip() else []
        except json.JSONDecodeError:
            return []  # Return empty list if JSON decoding fails

    # Load JSON fields safely
    output['heating_compare'] = safe_json_loads(form_detailed_data.heating_compare)
    output['cooling_compare'] = safe_json_loads(form_detailed_data.cooling_compare)

    # Convert to tuple format if necessary
    output['heating_compare'] = [tuple(value) for value in output['heating_compare']]
    output['cooling_compare'] = [tuple(value) for value in output['cooling_compare']]
    output['total_save_area'] = float(output['heat_save_area']) + float(output['cool_save_area'])
    # Debugging: Print only if 'Total_Savings' exists
    if 'Total_Savings' in output:
        print(output['Total_Savings'])
        print(f"total save area: {output['total_save_area']}")
        print(f"heat save area and cool save area {output['heat_save_area']} and {output['cool_save_area']}")

    return postdata_simple(request, output)


###################### DETAILED ########################################
def getCompletionStatus(request, pk):
    try: 
        form_detailed_data = Detailed_Data.objects.get(pk = pk)
    except Detailed_Data.DoesNotExist:
        return HttpResponse('Error in Simulation. Contact SysAdmin')
        # raise Exception('invalid pk')
    task_id = form_detailed_data.task_id
    result = AsyncResult(task_id)
    status = result.status
    form_detailed_data.result_status = status
    form_detailed_data.save()    
    if result.ready():
        return HttpResponse('true')
    else:
        return  HttpResponse('false') 

def redirectResults(request, pk):
    try: 
        form_detailed_data = Detailed_Data.objects.get(pk=pk)
    except Detailed_Data.DoesNotExist:
        return HttpResponse('Error in Simulation. Contact SysAdmin')
    
    output = {}

    # Extract field values
    for field in form_detailed_data._meta.get_fields():
        output[field.name] = getattr(form_detailed_data, field.name)

    # Helper function to safely load JSON fields
    def safe_json_loads(value):
        try:
            return json.loads(value) if value and value.strip() else []
        except json.JSONDecodeError:
            return []  # Return empty list if JSON decoding fails

    # Load JSON fields safely
    output['heating_compare'] = safe_json_loads(form_detailed_data.heating_compare)
    output['cooling_compare'] = safe_json_loads(form_detailed_data.cooling_compare)

    # Convert to tuple format if necessary
    output['heating_compare'] = [tuple(value) for value in output['heating_compare']]
    output['cooling_compare'] = [tuple(value) for value in output['cooling_compare']]

    # Debugging: Print only if 'Total_Savings' exists
    if 'Total_Savings' in output:
        print(output['Total_Savings'])

    return postdata_detailed(request, output)


########################### PARAMETRIC ##################################

def getCompletionStatusParametric(request, pk):
    try: 
        form_detailed_data = Parametric_Data.objects.get(pk = pk)
    except Parametric_Data.DoesNotExist:
        return HttpResponse('Error in Simulation. Contact SysAdmin')
        # raise Exception('invalid pk')
    task_id = form_detailed_data.task_id
    result = AsyncResult(task_id)
    status = result.status
    form_detailed_data.result_status = status
    form_detailed_data.save()    
    if result.ready():
        return HttpResponse('true')
    else:
        return  HttpResponse('false')

def redirectResultsParametric(request, pk):
    try: 
        form_detailed_data = Parametric_Data.objects.get(pk=pk)
    except Parametric_Data.DoesNotExist:
        return HttpResponse('Error in Simulation. Contact SysAdmin')
    output = {}
    # Extract field values
    for field in form_detailed_data._meta.get_fields():
        output[field.name] = getattr(form_detailed_data, field.name)

    # Helper function to safely load JSON fields
    def safe_json_loads(value):
        try:
            return json.loads(value) if value and value.strip() else []
        except json.JSONDecodeError:
            return []  # Return empty list if JSON decoding fails

    # Load JSON fields safely
    output['heating_compare'] = safe_json_loads(form_detailed_data.heating_compare)
    output['cooling_compare'] = safe_json_loads(form_detailed_data.cooling_compare)

    # Convert to tuple format if necessary
    output['heating_compare'] = [tuple(value) for value in output['heating_compare']]
    output['cooling_compare'] = [tuple(value) for value in output['cooling_compare']]

    # Debugging: Print only if 'Total_Savings' exists
    if 'Total_Savings' in output:
        print(output['Total_Savings'])

    return postdata_parametric(request, output)

#############################################################################################################################################

# User Registration
def create_user(request):
    register_form_name = request.POST.get("register-form-name","")
    register_form_email = request.POST.get("register-form-email","")
    register_form_username = request.POST.get("register-form-username","")
    register_form_phone = request.POST.get("register-form-phone","")
    register_form_password = request.POST.get("register-form-password","")
    
    if register_form_username and User.objects.filter(username=register_form_username):
        return redirect('login_register')
    user = User.objects.create_user(register_form_username,register_form_email, register_form_password)
    user.first_name = str(register_form_name)
    user.mobile = str(register_form_phone)
    user.save()
    print(user.id)
    print(user)
    print(user.email)
    
    user = authenticate(username = register_form_username, password = register_form_password)
    print(user)
    # print(user
    if user is not None:
        if user.is_active:
            login(request,user)
            return redirect('projects_page')
    return redirect('login_register')

# Login User
def login_user(request):
    email = request.POST.get("login-form-email","")
    password = request.POST.get("login-form-password","")
    print(email)
    user = authenticate(username=email, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return redirect('projects_page')
            
    else:
        print(user)
        return login_register(request)

# Logout user
def logout_user(request):
    logout(request)
    return redirect('CoolRoof')

# Send Email
def email(request):
    subject = 'Thank you for registering to our site'
    message = ' it  means a world to us '
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['sohrabemam01@gmail.com']
    send_mail( subject, message, email_from, recipient_list )



# base app
def CoolRoof(request,user = None):
    user = request.user
    return render(request, "CoolRoof.html",{'user':user})

def coolroof_detailed(request):
    return render(request, 'Coolroof_detailed.html')  # Rendering detailed page

def coolroof_parametric(request):
    return render(request, 'Coolroof_parametric.html') 
#def coolroof_detailed(request,user = None):
#    user = request.user
#    return render(request, "CoolRoof_detailed.html",{'user':user})
#def coolroof_parametric(request,user = None):
#    user = request.user
#   return render(request, "CoolRoof_parametric.html",{'user':user})
# Home page
def index_page(request,user = None):
    user = request.user
    return render(request, "index_page.html",{'user':user})

# Login page
def login_register(request):
    return render(request, "login_register.html")        

# Edit pages
def edit_page(request,pk):
    try: 
        edit_data = Simple.objects.filter(pk = pk).first()
    except edit_data.DoesNotExist:
        return HttpResponse('Simulation page doesnt exist. Contact SysAdmin')
    return render(request,"edit_page.html",{"edit_data":edit_data})

def edit_page_detailed(request,pk):
    try: 
        edit_data = Detailed_Data.objects.filter(pk = pk).first()
    except edit_data.DoesNotExist:
        return HttpResponse('Simulation page doesnt exist. Contact SysAdmin')
    return render(request,"edit_page_detailed.html",{"edit_data":edit_data})

def edit_page_parametric(request,pk):
    try: 
        edit_data = Parametric_Data.objects.filter(pk = pk).first()
    except edit_data.DoesNotExist:
        return HttpResponse('Simulation page doesnt exist. Contact SysAdmin')
    return render(request,"edit_page_parametric.html",{"edit_data":edit_data})
    


# Your projects page
@login_required(login_url='login_register')
def projects_page(request):
    user = request.user
    print(user)
    simple = Simple.objects.all().filter(username=user.username).values()
    detailed = Detailed_Data.objects.all().filter(username=user.username).values()
    parametric = Parametric_Data.objects.all().filter(username=user.username).values()
    
    # SESSION expires 50 mins (3000s).
    request.session.set_expiry(3000)
    
    return render( request,"projects_page.html",{'user':user,'simple':simple,'detailed':detailed,'parametric':parametric})        

# Data loaders & Display page after simulation 
def postdata_simple(request,output):
    return render(request,"post_simple.html",output)

def postdata_detailed(request,output):
    return render(request,"post_detailed.html",output)

def postdata_parametric(request,output):
    return render(request,"post_parametric.html",output)

def postdata_loader(request, pk):
    return render(request, "post_data_loader.html", {'pk':pk})

def postdata_loader_simple(request, pk):
    return render(request, "post_loader_simple.html", {'pk':pk})    

def postdata_loader_parametric(request, pk):
    return render(request, "post_loader_parametric.html", {'pk':pk})

def glossary(request):
    return render(request, "Glossary.html")    


# Django signup page (not used)
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})
