import pandas as pd
import simplejson
import numpy as np
from dateutil.relativedelta import relativedelta


def to_js_time(x):
    """
    turn number to javasctript datetime form, to highcharts x axis format
    :param x: one variable in datetime format - py
    :return: one variable in datetime format - js
    """
    y = (x - np.datetime64("1970-01-01 00:00:00")) / np.timedelta64(1, "s")
    return y * 1000


def clean_df(df, freq_int='MS'):
    # df.to_csv('df.csv')

    df = df[['date', 'value']]
    # try:
    #     un = df.columns[1].split(' ')[-1].strip('()')
    # except Exception as e:
    #     print(f'something went wrong while gettin unidade: {e}')
    #     un = ''
    # un = ''
    # df.columns = ['date', 'value']
    df.index = pd.to_datetime(df.date)
    dr = pd.date_range(start=df.index[0], end=df.index[-1], freq=freq_int)
    if freq_int == 'YS':
        dr = [d + relativedelta(month=10, day=1) for d in dr]
    df = df.reindex(dr)
    df.value = pd.to_numeric(df.value, errors='coerce')

    if freq_int == 'YS':
        chart_type = 'column'
    else:
        if df.value.isna().sum() > len(df)/2:
            chart_type = 'column'
        else:
            chart_type = 'line'

    dates = list(map(to_js_time, df.index))
    data_js = [list(x) for x in zip(dates, df.value)]
    return simplejson.dumps(data_js, ignore_nan=True),  chart_type


def get_model_from_parameter(param_id):
    """model 'manager'. get's a specific parameter model from SNIRH id (NOT local id) form model "Parametro".
       There might be a way of doing this better, but idk.


    Args:
        param_id (int):number identifying the param_id from snirh ids, NOT local 'Parametro' model id.

    Raises:
        ValueError: error

    Returns:
        django model: selected model
    """
    if param_id == 1436794570:
        from .models import PrecipitacaoMensal
        return PrecipitacaoMensal
    elif param_id == 413026594:
        from .models import PrecipitacaoDiaria
        return PrecipitacaoDiaria
    else:
        raise ValueError
