import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sb
from sklearn import preprocessing
from sklearn import linear_model

from dashboard.models import *
from dashboard.get_data import get_data

plt.ion()

mpl.rcParams['axes.labelsize'] = 20
mpl.rcParams['axes.titlesize'] = 24
mpl.rcParams['figure.figsize'] = (8, 4)
mpl.rcParams['xtick.labelsize'] = 14
mpl.rcParams['ytick.labelsize'] = 14
mpl.rcParams['legend.fontsize'] = 14


def stations_no_missing_data(df_, freq='MS', only_one=True):
    """Get stations data that have no missing data

    Args:
        df_ ([type]): [description]
    """
    df = df_.set_index('date')
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    df_final = pd.DataFrame()

    for station in df.station.unique():
        # print(f'Checking station {station}')
        df_s = df.loc[df.station == station]
        df_s.sort_index(inplace=True)
        idx_new = pd.date_range(start=min(df_s.index), end=max(df_s.index), freq=freq)
        if not any([True for i in idx_new if i not in df_s.index]):
            # print(f'--YES!')
            df_final = df_final.append(df_s)

    if only_one:
        df_count = pd.DataFrame(columns=['station', 'nr'])
        for s, df_s in df_final.groupby('station'):
            df_count.loc[len(df_count)] = [s, len(df_s)]

        stat_max = df_count.loc[df_count.nr == max(df_count.nr)]['station'].iloc[0]
        df_final = df_final.loc[df_final.station == stat_max]

    return df_final


def get_monthly_data(nr_stations=None):
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
    # df_total.to_csv('monthly_rainfall.csv')
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

    # df_total.to_csv('yearly_rainfall.csv')
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


def main2():
    df_all = pd.read_csv('monthly_rainfall.csv')
    df = stations_no_missing_data(df_all, freq='MS', only_one=True)
    y = df.rainfall

    y.plot()

    # SHOW WHAT WE WANT TO DO, PREDICT THE NEXT VALUE
    # known = y.loc['1930-01':'1930-12']
    # unknown = y.loc['1930-12':'1931-06']
    # to_predict = y.loc['1931-01':'1931-01']
    # fig, ax = plt.subplots()
    # known.plot(ax=ax, c='c', marker='o', zorder=3)
    # unknown.plot(ax=ax, c='grey', alpha=0.5)
    # to_predict.plot(ax=ax, c='r', marker='o', markersize=16, linestyle='')

    # ax.legend(['known', 'future', 'value to predict'])
    # ax.set_ylabel('# rainfall')

    # IF WE USE WINDOWS, THIS IS HOW IT SHOULD WORK
    # start = np.where(y.index == '1933-01-01 09:00:00')[0][0]
    # middle = np.where(y.index == '1939-01-01 09:00:00')[0][0]
    # end = np.where(y.index == '1940-12-01 09:00:00')[0][0]

    # window = 5
    # mult_factor = 50
    # fig, ax = plt.subplots()
    # for i in range(8):
    #     full = y.iloc[start:end]
    #     train =y.iloc[middle - i - window: middle - i].values
    #     predict = y.iloc[middle - i: middle - i + 1]
    #     (full + mult_factor*i).plot(ax=ax, c='grey', alpha=0.5)
    #     (train + mult_factor*i).plot(ax=ax, c='c', marker='o', markersize=4)
    #     (predict + mult_factor*i).plot(ax=ax, c='r', marker='o', markersize=8, linestyle='')

    window = 5
    num_samples = 8
    X_mat = []
    y_mat = []
    for i in range(num_samples):
        X_mat.append(y.iloc[middle - i - window: middle - i].values)
        y_mat.append(y.iloc[middle - i: middle - i + 1].values)

    X_mat = np.vstack(X_mat)
    y_mat = np.concatenate(y_mat)

    assert X_mat.shape == (num_samples, window)
    assert len(y_mat) == num_samples

    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score

    lr = LinearRegression(fit_intercept=False)
    lr = lr.fit(X_mat, y_mat)
    y_pred = lr.predict(X_mat)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(y_pred, y_mat)
    one_to_one = np.arange(y_mat.min() - 2, y_mat.max()+2)
    ax.set_xlim((one_to_one[0], one_to_one[-1]))
    ax.set_ylim((one_to_one[0], one_to_one[-1]))
    ax.set_xlabel('Predicted')
    ax.set_ylabel('True')
    ax.set_title(f'$R^{2}$ = {r2_score(y_mat, y_pred):3.2f}')


def other_main():
    from sktime.datasets import load_airline
    from sktime.forecasting.model_selection import temporal_train_test_split
    from sktime.utils.plotting.forecasting import plot_ys

    df = pd.read_csv('df_920752372.csv')
    y = df.rainfall
    y_train, y_test = temporal_train_test_split(y)
    plot_ys(y_train, y_test, labels=["y_train", "y_test"])

    from sktime.forecasting.naive import NaiveForecaster
    fh = 10
    naive_forecaster_last = NaiveForecaster(strategy="last")
    naive_forecaster_last.fit(y_train)
    y_last = naive_forecaster_last.predict(fh)

    naive_forecaster_seasonal = NaiveForecaster(strategy="seasonal_last", sp=12)
    naive_forecaster_seasonal.fit(y_train)
    y_seasonal_last = naive_forecaster_seasonal.predict(fh)

    plot_ys(y_train, y_test, y_last, y_seasonal_last, labels=[
            "y_train", "y_test", "y_pred_last", "y_pred_seasonal_last"])
    # smape_  loss(y_last, y_test)

    from sktime.forecasting.compose import ReducedRegressionForecaster
    from sklearn.ensemble import RandomForestRegressor
    regressor = RandomForestRegressor()
    forecaster = ReducedRegressionForecaster(regressor, window_length=12)
    forecaster.fit(y_train)
    y_pred = pd.Series()
    for i in range(100):
        y_pred = y_pred.append(forecaster.predict(i))

    plot_ys(y_train, y_test, y_pred, labels=['y_train', 'y_test', 'y_pred'])
    # smape_loss(y_test, y_pred)


def main3():
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from sktime.datasets import load_airline
    from sktime.forecasting.model_selection import temporal_train_test_split
    from sktime.performance_metrics.forecasting import smape_loss
    from sktime.utils.plotting.forecasting import plot_ys

    df = pd.read_csv('df_920752372.csv')
    y = df.rainfall

    fig, ax = plot_ys(y)
    ax.set(xlabel="Time", ylabel="rainfall")

    y_train, y_test = temporal_train_test_split(y, test_size=120)
    plot_ys(y_train, y_test, labels=["y_train", "y_test"])
    print(y_train.shape[0], y_test.shape[0])

    fh = np.arange(len(y_test)) + 1  # forecast horizon

    # TERRIBLE, based on last value only
    from sktime.forecasting.naive import NaiveForecaster
    forecaster = NaiveForecaster(strategy="last", sp=12)
    forecaster.fit(y_train)
    y_pred = forecaster.predict(fh)
    plot_ys(y_train, y_test, y_pred, labels=["y_train", "y_test", "y_pred"])
    smape_loss(y_pred, y_test)

    # BETTER, pretty good!
    from sktime.forecasting.compose import ReducedRegressionForecaster
    from sklearn.neighbors import KNeighborsRegressor
    regressor = KNeighborsRegressor(n_neighbors=1)
    forecaster = ReducedRegressionForecaster(regressor=regressor, window_length=12, strategy="recursive")
    forecaster.fit(y_train)
    y_pred = forecaster.predict(fh)
    plot_ys(y_train, y_test, y_pred, labels=["y_train", "y_test", "y_pred"])
    smape_loss(y_test, y_pred)

    # DOES NOT WORK
    from sktime.forecasting.exp_smoothing import ExponentialSmoothing
    forecaster = ExponentialSmoothing(trend="add", seasonal="multiplicative", sp=12)
    forecaster.fit(y_train)
    y_pred = forecaster.predict(fh)
    plot_ys(y_train, y_test, y_pred, labels=["y_train", "y_test", "y_pred"])
    smape_loss(y_test, y_pred)

    from sktime.forecasting.arima import AutoARIMA
    forecaster = AutoARIMA(sp=12, suppress_warnings=True)
    forecaster.fit(y_train)
    y_pred = forecaster.predict(fh)
    plot_ys(y_train, y_test, y_pred, labels=["y_train", "y_test", "y_pred"])
    smape_loss(y_test, y_pred)


def best_forecast(y, test_size=None):
    import numpy as np
    import pandas as pd
    from sktime.forecasting.model_selection import temporal_train_test_split
    from sktime.performance_metrics.forecasting import smape_loss
    from sktime.utils.plotting.forecasting import plot_ys
    from sktime.forecasting.compose import ReducedRegressionForecaster
    from sklearn.neighbors import KNeighborsRegressor
    # y = df.rainfall
    if not test_size:
        test_size = int(0.2*len(y))
    y_train, y_test = temporal_train_test_split(y, test_size=test_size)
    fh = np.arange(len(y_test)) + 1  # forecast horizon
    regressor = KNeighborsRegressor(n_neighbors=1)
    forecaster = ReducedRegressionForecaster(regressor=regressor, window_length=12, strategy="recursive")
    forecaster.fit(y_train)
    y_pred = forecaster.predict(fh)
    # plot_ys(y_train, y_test, y_pred, labels=["y_train", "y_test", "y_pred"])
    # return smape_loss(y_test, y_pred)
    return y_pred
# manguald
# estacao_id = 920685448
# df_ = pd.read_csv('monthly_rainfall.csv', index_col=0)
# df_s = df_.loc[df_.station == estacao_id]
# df = stations_no_missing_data(df_, only_one=False)
# df.to_csv('no_missing_data.csv')

# df = pd.read_csv('no_missing_data.csv')
# for s in df.station.unique()[:10]:
#     df_s = df.loc[df.station == s]
#     print(s)
#     try:
    # best_forecast(df_s.rainfall, int(len(df_s)*0.2))
#     except:
#         continue
