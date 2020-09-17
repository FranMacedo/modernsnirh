from django.contrib import admin
from .models import *
from leaflet.admin import LeafletGeoAdmin


class EstacaoAdmin(admin.ModelAdmin):
    search_fields = ['codigo', 'nome', 'latitude', 'altitude', 'bacia']


# Register your models here.
admin.site.register(Estacao, EstacaoAdmin)
admin.site.register(SessionData)
admin.site.register(SessionDataUnits)
admin.site.register(Parametro)
admin.site.register(ParametroUnit)
