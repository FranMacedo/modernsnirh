from django.contrib import admin
from .models import *
from leaflet.admin import LeafletGeoAdmin

# Register your models here.
admin.site.register(Estacao, LeafletGeoAdmin)
admin.site.register(SessionData)
admin.site.register(SessionDataUnits)
