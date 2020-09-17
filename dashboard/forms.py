from django import forms
from django.forms import ModelForm, ModelChoiceField
from .models import *


class RedeForm(forms.Form):
    rede = forms.ModelMultipleChoiceField(
        queryset=Rede.objects.all().order_by('nome'),
        widget=forms.SelectMultiple(attrs={'class': 'dd-select'}),
        label=''
    )


class EstacaoForm(forms.Form):
    estacao = forms.ModelMultipleChoiceField(
        queryset=Estacao.objects.filter(rede__slug='meteorologica').order_by('nome'),
        widget=forms.SelectMultiple(attrs={'class': 'dd-select'}),
        label=''
    )


class ParametroForm(forms.Form):
    estacoes = Estacao.objects.filter(rede__slug='meteorologica')
    parametros_ids = ParametroUnit.objects.filter(estacao__in=estacoes).values_list("parametro", flat=True).distinct()

    parametro = forms.ModelMultipleChoiceField(
        queryset=Parametro.objects.filter(id__in=parametros_ids).order_by('designacao'),
        widget=forms.SelectMultiple(attrs={'class': 'dd-select'}),
        label=''
    )


# class ParametroForm(forms.Form):

#     def __init__(self, *args, **kwargs):
#         super(ParametroForm, self).__init__(*args, **kwargs)

#         self.fields['parametros'] = forms.ModelMultipleChoiceField(
#             choices=Parametro.objects.all(),
#             # widget=forms.SelectMultiple(attrs={'class': 'dd-client'}),
#             # empty_label='Selecione a Instalação',
#             label=False,
#         )
