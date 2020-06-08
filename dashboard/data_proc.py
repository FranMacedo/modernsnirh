import pandas as pd
import simplejson
import numpy as np


def to_js_time(x):
    """
    turn number to javasctript datetime form, to highcharts x axis format
    :param x: one variable in datetime format - py
    :return: one variable in datetime format - js
    """
    y = (x - np.datetime64("1970-01-01 00:00:00")) / np.timedelta64(1, "s")
    return y * 1000


def clean_df(df, freq_int='MS'):
    df = df.iloc[:, :2]
    try:
        un = df.columns[1].split(' ')[-1].strip('()')
    except Exception as e:
        print(f'something went wrong while gettin unidade: {e}')
        un = ''
    df.columns = ['date', 'value']
    df.index = pd.to_datetime(df.date)
    df = df.reindex(pd.date_range(start=df.index[0], end=df.index[-1], freq=freq_int))
    df.value = pd.to_numeric(df.value, errors='coerce')
    dates = list(map(to_js_time, df.index))
    data_js = [list(x) for x in zip(dates, df.value)]
    return simplejson.dumps(data_js, ignore_nan=True), un
