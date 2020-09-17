import pandas as pd
import numpy as np
import json
from dashboard.models import *
pd.options.mode.chained_assignment = None  # default='warn'


def get_model_name(name_str):
    if name_str.upper() in ['ESTACAO', 'ESTAÇÃO', 'STATION', 'ESTACOES', 'ESTAÇÕES', 'STATIONS']:
        return Estacao
    elif name_str.upper() in ['PARAMETRO', 'PARÂMETRO', 'PARAMETROS', 'PARAMETERS', 'PARÂMETRO', 'PARAMETER']:
        return Parametro
    else:
        return None


def to_geom(row):
    try:
        return {'type': 'Point', 'coordinates': [json.dumps(row.longitude), json.dumps(row.latitude)]}
    except Exception as e:
        print(f"erro no geom: {e}")
        return {}


def get_estacao(est_id):
    return Estacao.objects.get(est_id=est_id)


def to_datetime(x):
    try:
        return pd.to_datetime(x)
    except:
        return None


def to_float(x):
    try:
        return float(x)
    except:
        return None


def df_to_estacao(df, date_col=[], replace=False):
    print(f'\n\n     :::!!filling Estacao Model!!:::      \n\n')

    ####### ALERT! #######
    ##Delete everything!##
    ######################

    # model.objects.all().delete()
    if not date_col:
        date_col = ['entrada_con', 'encerra_con', 'entrada_aut', 'encerra_aut']

    df['latitude'] = df['latitude'].map(to_float)
    df['longitude'] = df['longitude'].map(to_float)

    df['geom'] = None
    df['geom'] = df.apply(lambda row: to_geom(row), axis=1)

    for col in date_col:
        if col not in df.columns:
            continue
        try:
            df[col] = df[col].apply(lambda x: to_datetime(x))
            df[col] = df[col].replace({np.nan: None})
        except Exception as e:
            print(f"erro na conversão para dt-->  {e}")
            continue

    # turn fields that are supposed to be numbers
    for c in ['altitude', 'latitude', 'longitude', 'coord_x', 'coord_y']:
        if c in df.columns:
            df[c] = df[c].apply(lambda x: to_float(x))

    df = df.where(pd.notnull(df), None)

    # df = df.replace({np.nan:None}) #Isto transforma tudo em strings, o que estraga o geom por exemplo, no good. Só as datas!
    if replace:
        Estacao.objects.filter(est_id__in=df.est_id.tolist()).delete()
    else:
        est_id_vals = Estacao.objects.values_list('est_id', flat=True)
        df = df.loc[~df.est_id.isin(est_id_vals)]

    try:
        Estacao.objects.bulk_create(Estacao(**vals) for vals in df.to_dict("records"))
        print(f'\n\n     :::!!SUCCESS!!:::      \n\n')

    except Exception as e:
        print(f'\n\n     :::!!ERROR!!::: ----> Something went wrong: {e}\n\n')


def df_to_hidro(df, replace=False):
    print('filling HidroExtra Model')

    # df = df.replace({np.nan:None}) #Isto transforma tudo em strings, o que estraga o geom por exemplo, no good. Só as datas!
    df['estacao'] = df.est_id.apply(lambda x: get_estacao(x))
    for c in ['area_drenada']:
        if c in df.columns:
            df[c] = df[c].apply(lambda x: to_float(x))

    df = df.where(pd.notnull(df), None)

    if replace:
        HidroExtra.objects.filter(estacao__est_id__in=df.est_id.tolist()).delete()
    else:
        est_id_vals = HidroExtra.objects.values_list('estacao__est_id', flat=True)
        df = df.loc[~df.est_id.isin(est_id_vals)]

    df.drop(columns=['est_id'], inplace=True)

    try:
        HidroExtra.objects.bulk_create(HidroExtra(**vals) for vals in df.to_dict("records"))
        print(f'\n\n     :::!!SUCCESS!!:::      \n\n')

    except Exception as e:
        print(f'\n\n     :::!!ERROR!!::: ----> Something went wrong: {e}\n\n')


def file_to_model(file, model, date_col=[]):
    if isinstance(model, str):
        model = get_model_name(model)
    if not model:
        print(f'{model} in wrong format')
        return

    try:
        df = pd.read_csv(file, index_col=0, parse_dates=True)
    except Exception as e:
        print(f'Something went wrong: {e}')
        if '.csv' not in file:
            file = file + '.csv'
            print(f'--->Trying adding ".csv" extension: {file}')
            try:
                df = pd.read_csv(file, index_col=0, parse_dates=True)
            except Exception as e:
                print(f'Something went wrong AGAIN: {e}')
                return

    print('file read successfuly')
    df.drop('id', axis=1, inplace=True)
    print(f'going for the model {model}')
    df_to_model(df, model, date_col)
