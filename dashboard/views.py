from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import *
from djgeojson.serializers import Serializer as GeoJSONSerializer
from .forms import EstacaoForm, ParametroForm
import json
from .get_data import get_data
from .data_proc import clean_df
import time
from django_pandas.io import read_frame


def index(request):
    print('here!')
    if request.method == 'POST':

        response_body = json.loads(request.body)
        est_id = response_body.get('stat_id')
        param_id = response_body.get('param_id')
        print(est_id, param_id)
        if not est_id or not param_id:
            return JsonResponse({'stat': 'false'})

        # SelectedEstacao.objects.all().delete()

        station = get_object_or_404(Estacao, id=int(est_id))
        parameter = get_object_or_404(Parametro, id=int(param_id))

        qs = SessionData.objects.filter(estacao=station, parametro=parameter)

        if not qs:
            print('sem dados na session db')
            df, result = get_data(estacao=station.est_id, parametro=parameter.param_id)
            print(df.head())
            try:
                un = df.columns[1].split(' ')[-1].strip('()')
            except:
                un = ''
            if not result:
                return JsonResponse({'stat': 'false', 'station_name': station.nome, 'parameter_name': parameter.designacao})
            df.columns = ['date', 'value']

            if df.value.isna().sum() == len(df):
                return JsonResponse({'stat': 'false', 'station_name': station.nome, 'parameter_name': parameter.designacao})

            df['estacao'] = station
            df['parametro'] = parameter

            SessionData.objects.bulk_create(SessionData(**vals) for vals in df.to_dict('records'))
            SessionDataUnits.objects.create(
                estacao=station,
                parametro=parameter,
                un=un
            ).save()
        else:
            print('ja com dados na db!:')
            df = read_frame(qs)
            df = df[['date', 'value']]
            try:
                un = SessionDataUnits.objects.get(estacao=station, parametro=parameter).un
            except:
                un = ''
        print(df.value)
        data, chart_type = clean_df(df, freq_int=parameter.freq)

        return JsonResponse({'stat': 'true',
                             'data': data,
                             'station_name': station.nome,
                             'parameter_name': parameter.designacao,
                             'un': un,
                             'chartType': chart_type
                             })
        # try:
        #     station = Estacao.objects.get(id=est_id)
        # except Exception as e:
        #     print(f'fake station: {e}')

        # try:
        #     parameter = Parametro.objects.get(id=param_id)
        # except Exception as e:
        #     print(f'fake parameter: {e}')

        # if station and parameter:
        #     df, result = get_data(estacao=station.est_id, parametro=parameter.param_id)

        #     if not result:
        #         return JsonResponse({'stat': 'false'})

        #     data, un = clean_df(df, freq_int=parameter.freq)
        #     station_name = station.nome
        #     parameter_name = parameter.designacao

        #     return JsonResponse({'stat': 'true',
        #                          'data': data,
        #                          'station_name': station_name,
        #                          'parameter_name': parameter_name,
        #                          'un': un
        #                          })
        # else:
        #     return JsonResponse({'stat': 'false'})

    # if a GET (or any other method) we'll create a blank form
    else:
        estacao_form = EstacaoForm()
        parametro_form = ParametroForm()
        SessionData.objects.all().delete()
    # print(Estacao.objects.all())
    return render(request, 'index.html', {'estacao_form': estacao_form, 'parametro_form': parametro_form})
# Create your views here.


def data_map(request):
    context = Estacao.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    # context = Estacao.objects.first()

    # We also want to show data for instalacoes that have no coordinates, even if they are not represented in the map
    # context = Instalacao.user_allowed(request.user).select_related('gestao')

    data = GeoJSONSerializer().serialize(context, use_natural_keys=True, with_modelname=False, properties=(
        "codigo", "nome", "id", "altitude", "latitude", "longitude", 'popupContent'))
    return HttpResponse(data)


def testando(request):
    print('inicio!')
    time.sleep(2)
    print('fim')
    return JsonResponse({'data': 'data'})

    # def index(request):
    #     if request.method == 'POST':
    #         # create a form instance and populate it with data from the request:
    #         estacao_form = EstacaoForm(request.POST)
    #         parametro_form = ParametroForm(request.POST)

    #         estacao_valid = estacao_form.is_valid()
    #         parametro_valid = parametro_form.is_valid()
    #         print('\n\nISVALID :', parametro_valid, '\n\n')
    #         # check whether it's valid:
    #         if estacao_valid and parametro_valid:
    #             data = {}
    #             for e in estacao_form.cleaned_data['estacao']:
    #                 print(e.id)
    #                 data[e.id] = {}
    #                 for p in parametro_form.cleaned_data['parametro']:
    #                     print(p.freq)
    #                     df, result = get_data(estacao=e.est_id, parametro=p.param_id)
    #                     data[e.id][p.id] = clean_df(df, freq_int=p.freq)

    #             print(data)
    #             if not result:
    #                 return JsonResponse({'stat': 'false'})

    #             # process the data in form.cleaned_data as required
    #             # ...
    #             # redirect to a new URL:
    #             return JsonResponse({'stat': 'true', 'data': data})

    #     # if a GET (or any other method) we'll create a blank form
    #     else:
    #         estacao_form = EstacaoForm()
    #         parametro_form = ParametroForm()
    #     # print(Estacao.objects.all())
    #     return render(request, 'index.html', {'estacao_form': estacao_form, 'parametro_form': parametro_form})
    # # Create your views here.
