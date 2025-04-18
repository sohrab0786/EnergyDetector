"""CoolRoof URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from . import views
admin.site.site_header = "CoolRoof"
admin.site.site_title = "CBS"
admin.site.index_title = "Home"
urlpatterns = [
    re_path(r'^admin/',admin.site.urls),
    re_path(r'^Coolroof/',views.coolroof),
    re_path(r'^Calculator/',include("Calculator.urls")),
    re_path(r'^EPlus/',include("EPlus.urls")),

]
