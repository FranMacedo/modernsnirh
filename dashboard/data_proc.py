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


def get_freq(date_diff):
    freq = min(date_diff)
    freq_days = freq.days
    if freq_days < 1:
        return 'H'
    elif freq_days == 1:
        return 'D'
    elif freq_days < 32:
        return 'MS'
    else:
        return 'YS'


def clean_df(df):
    # print(df)

    df = df[['date', 'value']]
    df = df.sort_values('date')
    # from .forecast import best_forecast
    # y_pred = best_forecast(df.value, int(0.2*len(df)))

    df.index = pd.to_datetime(df.date)
    freq = get_freq(df.date.diff()[1:])

    dr = pd.date_range(start=df.index[0], end=df.index[-1], freq=freq)
    # dr_pred = pd.date_range(start=df.index[-1] + relativedelta(months=1),
    # end=df.index[-1] + relativedelta(months=len(y_pred)), freq=freq)

    # if freq == 'YS':
    #     dr = [d + relativedelta(month=10, day=1) for d in dr]
    #     dr2 = [d for d in dr if not any([i.month==d.month and i.year==d.year  for i in df.index])]
    dr = list(dr) + list(df.index)
    dr = list(set(dr))

    df = df.reindex(dr)
    df.sort_index(inplace=True)
    if freq == 'YS':
        df['year'] = df.index.year
        df.date = df.index
        df.reset_index(drop=True, inplace=True)
        df_dup = df.loc[df.year.duplicated(keep=False)]
        idx_drop = df_dup[df_dup.value.isna()].index
        df = df.loc[~df.index.isin(idx_drop)]
        df.index = df.date
        df.drop(columns=['year'], inplace=True)

    elif freq == 'MS':
        df['ym'] = df.index.year.map(str) + df.index.month.map(str)
        df.date = df.index
        df.reset_index(drop=True, inplace=True)
        df_dup = df.loc[df.ym.duplicated(keep=False)]
        idx_drop = df_dup[df_dup.value.isna()].index
        df = df.loc[~df.index.isin(idx_drop)]
        df.index = df.date
        df.drop(columns=['ym'], inplace=True)

    df.value = pd.to_numeric(df.value, errors='coerce')

    if freq == 'YS':
        chart_type = 'column'
    else:
        if df.value.isna().sum() > len(df)*0.3:
            chart_type = 'column'
        else:
            chart_type = 'line'

    df.drop(columns=['date'], inplace=True)
    # df.to_csv('dft.csv')
    # y_pred.to_csv('y_pred.csv')
    # df = pd.read_csv('dft.csv', index_col=0, parse_dates=True)
    # y_pred = pd.read_csv('y_pred.csv', index_col=0, parse_dates=True)
    # print(y_pred)

    dates = list(map(to_js_time, df.index))
    data_js = [list(x) for x in zip(dates, df.value)]

    # dates_pred = list(map(to_js_time, dr_pred))
    # data_js_pred = [list(x) for x in zip(dates_pred, y_pred)]

    # return simplejson.dumps(data_js, ignore_nan=True), simplejson.dumps(data_js_pred, ignore_nan=True),  chart_type
    return simplejson.dumps(data_js, ignore_nan=True),   chart_type


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
