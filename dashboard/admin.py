from django.contrib import admin
from .models import Estacao
from leaflet.admin import LeafletGeoAdmin

# Register your models here.
admin.site.register(Estacao, LeafletGeoAdmin)