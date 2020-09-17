import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sb
from sklearn import preprocessing
from sklearn import linear_model

from dashboard.models import *
from dashboard.get_data import get_data


def get_monthly_data():
    df_total = pd.DataFrame()
    all_meteo_stations = Estacao.objects.filter(rede__slug='meteorologica')
    for estacao in all_meteo_stations:
        # estacao = all_meteo_stations[0]
        df, result = get_data(estacao=estacao.est_id, parametro=1436794570)
        if not result:
            continue
        print('--success!')
        df['estacao'] = estacao.est_id
        df_total = df_total.append(df)

    df_total.reset_index(inplace=True, drop=True)
    df_total.columns = ['date', 'rainfall', 'station']
    df_total.to_csv('monthly_rainfall.csv')
    return df_total


def get_yearly_data():
    df_total = pd.DataFrame()
    all_meteo_stations = Estacao.objects.filter(rede__slug='meteorologica')
    for estacao in all_meteo_stations:
        df, result = get_data(estacao=estacao.est_id, parametro=4237)
        if not result:
            continue
        print('--success!')
        df['estacao'] = estacao.est_id
        df_total = df_total.append(df)
    df_total.reset_index(inplace=True, drop=True)
    df_total.columns = ['date', 'rainfall', 'station']
    df_total['year'] = df_total.date.dt.year
    df_total.drop(columns='date', inplace=True)
    df_total.rainfall = df_total.rainfall.map(float)

    df_total.to_csv('yearly_rainfall.csv')
    return df_total


def reshape_data(df):
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df.date.dt.year
    df['month'] = df.date.dt.month
    df['year_station'] = df['station'].map(str) + ' - ' + df['year'].map(str)
    df_r = df.pivot(index='year_station', columns='month', values='rainfall')
    df_r.reset_index(inplace=True, drop=False)
    df_r['station'] = df_r.year_station.apply(lambda x: x.split('-')[0].strip())
    df_r['year'] = df_r.year_station.apply(lambda x: x.split('-')[1].strip())
    df_r.drop(columns='year_station', inplace=True)
    for c in df_r.columns:
        if c in ['station', 'year']:
            df_r[c] = df_r[c].map(int)
            continue
        df_r[c] = df_r[c].map(float)
    return df_r


def predict_results(lm, x_vals, y_vals, do_plot=False, plot_name=''):
    pred = lm.predict(x_vals)
    # print(test_y)
    # print(pred)
    print("Mean Squared Error: ", mean_squared_error(y_vals, pred))
    print("Root Mean Squared Error: ", np.sqrt(mean_squared_error(y_vals, pred)))
    print("r2_score: ", r2_score(y_vals, pred))
    print("Mean Absolute Error: ", mean_absolute_error(y_vals, pred))
    # plt.scatter(pred, test_y)
    # plt.xlabel('TRAIN_X')
    # plt.ylabel('TRAIN_Y')
    # plt.show()
    if do_plot:
        residuals = pred-y_vals
        # print('MAD (Training Data): ' + str(np.mean(np.abs(residuals))))
        df_res = pd.DataFrame(residuals)
        df_res.columns = ['Residuals']
        fig = plt.figure(figsize=(18, 10))
        ax = fig.add_subplot(111)
        df_res.plot.line(title=f'Different b/w Actual and Predicted ({plot_name})', color='c', ax=ax, fontsize=20)
        ax.xaxis.set_ticklabels([])
        plt.ylabel('Residual')
        ax.title.set_fontsize(30)
        ax.xaxis.label.set_fontsize(20)
        ax.yaxis.label.set_fontsize(20)


def predict_based_last_months(n_months, df, do_plot=False):
    print(f"\n\n___Multiple Linear regression model predict based on last {n_months} months___\n\n")
    col_nrs = range(1, n_months+1)
    df2 = df[['station'] + list(col_nrs)]
    col_names = ['station'] + [f'x{c}' for c in col_nrs]
    col_names[-1] = 'y'
    df2.columns = np.array(col_names)
    for k in range(2, 12-n_months+2):
        df3 = df[['station'] + [k+i for i in range(0, n_months)]]
        df3.columns = np.array(col_names)
        df2 = df2.append(df3)
    df2.index = range(df2.shape[0])
    y = df2['y']
    x = df2[col_names[:-1]]
    train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.3, shuffle=False)
    # print("Train x shape", train_x.shape, "; Test_x", test_x.shape)
    # print("Train y shape", train_y.shape, "; Test_y", test_y.shape)
    lm = linear_model.LinearRegression()
    lm.fit(train_x, train_y)
    print('TRAINING RESULTS:')
    predict_results(lm, train_x, train_y, do_plot, 'training data')
    print('\n TESTING RESULTS:')
    predict_results(lm, test_x, test_y, do_plot, 'testing data')
    plt.show()


def main(has_excel=True):
    # GATHER DATA
    if has_excel:
        df = pd.read_csv('monthly_rainfall.csv')
    else:
        df = get_monthly_data()

    # RESHAPE DATA
    df = reshape_data(df)

    # Maybe use anual rainfall?
    # df_y = get_yearly_data()
    # df = pd.merge(df, df_y, how='left', left_on=['station', 'year'], right_on=['station', 'year'])
    # df.rename(columns={'rainfall': 'anual'}, inplace=True)
    # df[range(1, 13)].sum(axis=1) - df.anual

    # for now, sum it up

    # FILL MISSING VALUES
    # muito generalista
    # df_r.fillna(np.mean(df_r))
    for station in df.station.unique():
        df_station = df.loc[df.station == station, :]
        df.loc[df.station == station, :] = df_station.fillna(np.mean(df_station))

    predict_based_last_months(12, df, False)
    # df['anual'] = df[range(1, 13)].sum(axis=1)

    # print('\nnull values:')
    # print(df.isnull().sum())
    # print('\ndf info:')
    # print(df.info())
    # print(df.groupby('station').size())
    # print("Co-Variance:\n", df.cov())
    # print("Co-Relation:\n", df.corr())

    # corr_cols = df.corr()['anual'].sort_values()[::-1]
