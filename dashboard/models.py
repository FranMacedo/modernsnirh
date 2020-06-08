from django.db import models

# Create your models here.
# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User
from djgeojson.fields import PointField

# Create your models here.


class Estacao(models.Model):
    codigo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Código")
    nome = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nome")
    altitude = models.FloatField(max_length=100, blank=True, null=True, verbose_name="Altitude")
    latitude = models.FloatField(max_length=100, blank=True, null=True, verbose_name="Latitude")
    longitude = models.FloatField(max_length=100, blank=True, null=True, verbose_name="Longitude")
    coord_x = models.FloatField(max_length=100, blank=True, null=True, verbose_name="Coordenada X")
    coord_y = models.FloatField(max_length=100, blank=True, null=True, verbose_name="Coordenada Y")
    bacia = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bacia")
    distrito = models.CharField(max_length=100, blank=True, null=True, verbose_name="Distrito")
    concelho = models.CharField(max_length=100, blank=True, null=True, verbose_name="Concelho")
    freguesia = models.CharField(max_length=100, blank=True, null=True, verbose_name="Freguesia")
    responsavel_aut = models.CharField(max_length=100, blank=True, null=True,
                                       verbose_name="Entidade Responsável Automático",)
    responsavel_con = models.CharField(max_length=100, blank=True, null=True,
                                       verbose_name="Entidade Responsável Convencional")
    estacao_aut = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tipo de Estação Automática")
    estacao_con = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tipo de Estação Convencional")
    entrada_con = models.DateTimeField(blank=True, null=True, verbose_name="Entrada Funcionamento Convencional")
    encerra_con = models.DateTimeField(blank=True, null=True, verbose_name="Encerramento Convencional")
    entrada_aut = models.DateTimeField(blank=True, null=True, verbose_name="Entrada Funcionamento Automática")
    encerra_aut = models.DateTimeField(blank=True, null=True, verbose_name="Encerramento Automática")
    telemetria = models.CharField(max_length=100, blank=True, null=True, verbose_name="Telemetria")
    estado = models.CharField(max_length=100, blank=True, null=True, verbose_name="Estado")
    est_id = models.BigIntegerField(verbose_name="Estação ID", default=0)
    geom = PointField(blank=True, null=True)

    @property
    def popupContent(self):
        return f'<div><div>{self.nome}</div><div>{self.codigo}</div></div>'

    def __str__(self):
        return str(self.codigo) + " - " + str(self.nome)


class Parametro(models.Model):
    param_id = models.BigIntegerField(verbose_name="Parametro ID", default=0)
    designacao = models.CharField(max_length=100, blank=True, null=True, verbose_name="Designacao")
    freq = models.CharField(max_length=10, blank=True, null=True, verbose_name="Frequencia")

    def __str__(self):
        return str(self.designacao)
