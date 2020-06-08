import pandas as pd
import numpy as np
import json
from dashboard.models import *


def get_model_name(name_str):
    if name_str.upper() in ['ESTACAO', 'ESTAÇÃO', 'STATION', 'ESTACOES', 'ESTAÇÕES', 'STATIONS']:
        return Estacao
    elif name_str.upper() in ['PARAMETRO', 'PARÂMETRO', 'PARAMETROS', 'PARAMETERS', 'PARÂMETRO', 'PARAMETER']:
        return Parametro
    else:
        return None


def to_geom(row):
    print(row)
    try:
        return {'type': 'Point', 'coordinates': [json.dumps(row.longitude), json.dumps(row.latitude)]}
    except Exception as e:
        print(f"erro no geom: {e}")
        return {}


def df_to_model(df, model, date_col=[]):
    if isinstance(model, str):
        model = get_model_name(model)

    if not model:
        print(f'{model} in wrong format')
        return

    ####### ALERT! ####### 
    ##Delete everything!##
    ######################

    model.objects.all().delete()
    if not date_col:
        date_col = ['entrada_con', 'encerra_con', 'entrada_aut', 'encerra_aut']

    if 'geom' in df.columns:
        df['geom'] = df.apply(lambda row: to_geom(row), axis=1)
    print(df.geom)
    for col in date_col:
        if col not in df.columns:
            continue
        try:
            df[col] = pd.to_datetime(df[col])
            df[col] = df[col].replace({np.nan:None})
        except Exception as e:
            print(f"erro na conversão para dt-->  {e}")
            continue
    df = df.where(pd.notnull(df), None)
    print(df.geom)
    # df = df.replace({np.nan:None}) #Isto transforma tudo em strings, o que estraga o geom por exemplo, no good. Só as datas!
    try:
        model.objects.bulk_create(model(**vals) for vals in df.to_dict("records"))
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
