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
from django.utils.text import slugify

# Create your models here.


# class EstacaoLower(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(author='Roald Dahl')


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
        return str(self.codigo) + " - " + str(self.nome).title()


class Parametro(models.Model):
    param_id = models.BigIntegerField(verbose_name="Parametro ID", default=0)
    designacao = models.CharField(max_length=100, blank=True, null=True, verbose_name="Designacao")
    freq = models.CharField(max_length=10, blank=True, null=True, verbose_name="Frequencia")
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.designacao)
        super(Parametro, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.designacao)


class SessionData(models.Model):
    estacao = models.ForeignKey(Estacao, on_delete=models.CASCADE, blank=True, null=True)
    parametro = models.ForeignKey(Parametro, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)  # date of value
    value = models.FloatField(max_length=100, blank=True, null=True)  # value of parameter

    def __str__(self):
        return str(self.estacao.nome) + '-' + str(self.parametro.designacao)


class SessionDataUnits(models.Model):
    estacao = models.ForeignKey(Estacao, on_delete=models.CASCADE, blank=True, null=True)
    parametro = models.ForeignKey(Parametro, on_delete=models.CASCADE, blank=True, null=True)
    un = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return str(self.estacao.nome) + '-' + str(self.parametro.designacao)


class PrecipitacaoMensal(models.Model):
    estacao = models.ForeignKey(Estacao, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)  # date of value
    value = models.FloatField(max_length=100, blank=True, null=True)  # value of parameter

    def __str__(self):
        return str(self.estacao.nome)


class PrecipitacaoDiaria(models.Model):
    estacao = models.ForeignKey(Estacao, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)  # date of value
    value = models.FloatField(max_length=100, blank=True, null=True)  # value of parameter

    def __str__(self):
        return str(self.estacao.nome)


class EstacaoParamUnits(models.Model):
    estacao = models.ForeignKey(Estacao, on_delete=models.CASCADE, blank=True, null=True)
    parametro = models.ForeignKey(Parametro, on_delete=models.CASCADE, blank=True, null=True)
    un = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return str(self.estacao.nome) + '-' + str(self.parametro.designacao)
