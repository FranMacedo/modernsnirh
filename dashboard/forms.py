from django import forms
from django.forms import ModelForm, ModelChoiceField
from .models import Estacao, Parametro


class EstacaoForm(forms.Form):
    estacao = forms.ModelMultipleChoiceField(
        queryset=Estacao.objects.all().order_by('nome'),
        widget=forms.SelectMultiple(attrs={'class': 'dd-select'}),
        label=''
    )


class ParametroForm(forms.Form):
    parametro = forms.ModelMultipleChoiceField(
        queryset=Parametro.objects.all().order_by('designacao'),
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
