from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import *
from djgeojson.serializers import Serializer as GeoJSONSerializer
from .forms import EstacaoForm, ParametroForm
import json
from .get_data import get_data
from .data_proc import clean_df, get_model_from_parameter
import time
from django_pandas.io import read_frame
from .secret_vars import gmaps_api_key, mapbox_access_token
from datetime import datetime
import pandas as pd


def index(request):
    # print('here!')
    if request.method == 'POST':
        try:
            response_body = json.loads(request.body)
            start_date = response_body.get('start_date')
            end_date = response_body.get('end_date')
            if start_date == '':
                start_date = datetime(1930, 1, 1)
            else:
                start_date = pd.to_datetime(start_date, format='%d/%m/%Y')

            if end_date == '':
                end_date = datetime.now()
            else:
                end_date = pd.to_datetime(end_date, format='%d/%m/%Y')

            est_id_local = response_body.get('stat_id')
            param_id_local = response_body.get('param_id')
            print(est_id_local, param_id_local)
            if not est_id_local or not param_id_local:
                return JsonResponse({'stat': 'false'})

            station = get_object_or_404(Estacao, id=int(est_id_local))
            parameter = get_object_or_404(Parametro, id=int(param_id_local))
            has_model = False
            has_qs = False
            try:
                # check if model exists
                selected_model = get_model_from_parameter(parameter.param_id)
                selected_model_un = EstacaoParamUnits
                has_model = True
            except ValueError:
                # if not, check/save in session data
                selected_model_un = SessionDataUnits

            if has_model:
                # even if it has a model, it can has no data
                qs = selected_model.objects.filter(estacao=station, date__gte=start_date, date__lte=end_date)
                has_qs = True
                if not qs:
                    has_qs = False
                    has_model = False
                    selected_model_un = SessionDataUnits

            if not has_qs:
                qs = SessionData.objects.filter(estacao=station, parametro=parameter,
                                                date__gte=start_date, date__lte=end_date)

            if not qs:
                # print('sem dados na session db')
                df, result = get_data(estacao=station.est_id, parametro=parameter.param_id,
                                      date_begin=start_date, date_end=end_date)
                # print(df.head())
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
                try:
                    SessionData.objects.bulk_create(SessionData(**vals) for vals in df.to_dict('records'))
                    SessionDataUnits.objects.create(
                        estacao=station,
                        parametro=parameter,
                        un=un
                    ).save()
                except:
                    pass

            else:
                # print('ja com dados na db!:')
                df = read_frame(qs)
                df = df[['date', 'value']]
                try:
                    un = selected_model_un.objects.get(estacao=station, parametro=parameter).un
                except:
                    un = ''
            # print(df.value)
            data, chart_type = clean_df(df, freq_int=parameter.freq)

            return JsonResponse({'stat': 'true',
                                 'data': data,
                                 'station_name': station.nome,
                                 'parameter_name': parameter.designacao,
                                 'un': un,
                                 'chartType': chart_type
                                 })
        except Exception as e:
            return JsonResponse({'stat': 'error', 'msg': str(e)})
    # if a GET (or any other method) we'll create a blank form
    else:
        estacao_form = EstacaoForm()
        parametro_form = ParametroForm()
        SessionData.objects.all().delete()
        SessionDataUnits.objects.all().delete()
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("vacuum;")

        all_params = Parametro.objects.all()
        large_params = [p.id for p in all_params if 'hora' in p.slug or 'dia' in p.slug]
        # quit()
    # print(Estacao.objects.all())
    return render(request, 'index.html', {'estacao_form': estacao_form, 'parametro_form': parametro_form, 'gmaps_api_key': gmaps_api_key, 'mapbox_access_token': mapbox_access_token, 'large_params': large_params})
# Create your views here.


def data_map(request):
    context = Estacao.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    # context = Estacao.objects.first()

    # We also SHOULD want to show data for instalacoes that have no coordinates, even if they are not represented in the map

    data = GeoJSONSerializer().serialize(context, use_natural_keys=True, with_modelname=False, properties=(
        "codigo", "nome", "id", "altitude", "latitude", "longitude", 'popupContent'))
    return HttpResponse(data)


def testando(request):
    # print('inicio!')
    return render(request, 'index_2.html')
