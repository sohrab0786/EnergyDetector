from django.contrib import admin

# Register your models here.
from Calculator.models import Simple

from Calculator.models import Detailed_Data
from Calculator.models import Parametric_Data

admin.site.register(Simple)

admin.site.register(Detailed_Data)
admin.site.register(Parametric_Data)
