from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.stattools import acf, pacf
from dashboard.forecast import *
from statsmodels.tsa.stattools import adfuller
from pylab import rcParams
import matplotlib
import statsmodels.api as sm
import pandas as pd
import warnings
import itertools
import numpy as np
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")
plt.style.use('fivethirtyeight')
matplotlib.rcParams['axes.labelsize'] = 14
matplotlib.rcParams['xtick.labelsize'] = 12
matplotlib.rcParams['ytick.labelsize'] = 12
matplotlib.rcParams['text.color'] = 'k'


def test_stationarity(timeseries):
   # Determing rolling statistics
    rolmean = timeseries.rolling(window=12).mean()
    rolstd = timeseries.rolling(window=12).std()
    # Plot rolling statistics:
    orig = plt.plot(timeseries, color='blue', label='Original')
    mean = plt.plot(rolmean, color='red', label='Rolling Mean')
    std = plt.plot(rolstd, color='black', label='Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean & Standard Deviation')
    plt.show(block=False)
    # Perform Dickey-Fuller test:
    print('Results of Dickey-Fuller Test:')
    dftest = adfuller(timeseries, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic', 'p-value', '#Lags Used', 'Number of Observations Used'])
    for key, value in dftest[4].items():
        dfoutput['Critical Value (%s)' % key] = value
    print(dfoutput)
    print("""\n         ------------ INTERPERTATION -------------- 
    
      If the ‘Test Statistic’ is less than the ‘Critical Value’, 
      we can reject the null hypothesis and say that the series is stationary.

      \n\n STATIONARY SERIES SHOULD HAVE:
       - constant mean
       - constant variance
       - an autocovariance that does not depend on time.
    """)


df = pd.read_csv('monthly_rainfall.csv')
df = df[['date', 'rainfall', 'station']]
df['date'] = pd.to_datetime(df.date)
df['station'] = df.station.map(str)
df.set_index('date', inplace=True)

min_null = 10000
df_results = pd.DataFrame(columns=['station', 'null_vals', 'months_avai'])
for i, df_s in df.groupby('station'):
    print(i)
    months_avai = len(df_s)
    null_vals = df_s.asfreq('MS').isna().sum()['rainfall']
    df_results.loc[len(df_results)] = [i, null_vals, months_avai]
    # rainfall.isna().sum()

best_station = df_results.loc[df_results.null_vals == 0].sort_values('months_avai', ascending=False).iloc[0]['station']
station = df.loc[df.station == best_station][['rainfall']]
station.sort_index(inplace=True)
station.isnull().sum()
y = station.asfreq('MS')
test_stationarity(y)

lag_acf = acf(y, nlags=20)
lag_pacf = pacf(y, nlags=20, method='ols')
plt.subplot(121)
plt.plot(lag_acf)
plt.axhline(y=0, linestyle='--', color='gray')
plt.axhline(y=-1.96/np.sqrt(len(y)), linestyle='--', color='gray')
plt.axhline(y=1.96/np.sqrt(len(y)), linestyle='--', color='gray')
plt.title('Autocorrelation Function')

plt.subplot(122)
plt.plot(lag_pacf)
plt.axhline(y=0, linestyle='--', color='gray')
plt.axhline(y=-1.96/np.sqrt(len(y)), linestyle='--', color='gray')
plt.axhline(y=1.96/np.sqrt(len(y)), linestyle='--', color='gray')
plt.title('Partial Autocorrelation Function')
plt.tight_layout()

plt.show(block=False)

# AR MODEL
model = ARIMA(y, order=(2, 1, 0))
results_AR = model.fit(disp=-1)
plt.plot(y)
plt.plot(results_AR.fittedvalues, color='red')
# plt.title('RSS: %.4f'% sum((results_AR.fittedvalues-y)**2))

# MA MODEL
model = ARIMA(y, order=(0, 1, 2))
results_MA = model.fit(disp=-1)
plt.plot(y)
plt.plot(results_MA.fittedvalues, color='red')
# plt.title('RSS: %.4f'% sum((results_MA.fittedvalues-ts_log_diff)**2))

model = ARIMA(y, order=(2, 0, 3))
results_ARIMA = model.fit(disp=-1)
plt.plot(y)
plt.plot(results_ARIMA.fittedvalues, color='red')
# plt.title('RSS: %.4f'% sum((results_ARIMA.fittedvalues-ts_log_diff)**2))
plt.show(block=False)


# Fill missing values as mean of last 10 year and forward 5 years.... because??
for i, row_miss in y[y.rainfall.isna()].iterrows():
    val = y.loc[(y.index.month == i.month) & (y.index.year >= i.year - 3)
                & (y.index.year <= i.year + 3)].rainfall.mean()
    # print(val)
    y.loc[i] = val
y.plot(figsize=(15, 6))
plt.show()

rcParams['figure.figsize'] = 18, 8
decomposition = sm.tsa.seasonal_decompose(y, model='additive')
fig = decomposition.plot()
plt.show()

p = d = q = range(0, 2)
pdq = list(itertools.product(p, d, q))
seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]
print('Examples of parameter combinations for Seasonal ARIMA...')
print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[1]))
print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[2]))
print('SARIMAX: {} x {}'.format(pdq[2], seasonal_pdq[3]))
print('SARIMAX: {} x {}'.format(pdq[2], seasonal_pdq[4]))

fit_results = pd.DataFrame(columns=['param', 'param_seasonal', 'AIC'])
for param in pdq:
    for param_seasonal in seasonal_pdq:
        try:
            mod = sm.tsa.statespace.SARIMAX(y,
                                            order=param,
                                            seasonal_order=param_seasonal,
                                            enforce_stationarity=False,
                                            enforce_invertibility=False)
            results = mod.fit()
            print('ARIMA{}x{}12 - AIC:{}'.format(param, param_seasonal, results.aic))
            fit_results.loc[len(fit_results)] = [param, param_seasonal, results.aic]
        except:
            continue

# print('\n'.join(fit_results))

# best resuls === lower AIC. for example: ARIMA(1, 1, 1)x(0, 1, 1, 12)12 - AIC:281.3873006939412
# best_param = (1, 1, 1)
# best_param_seasonal = (0, 1, 1, 12)

best_AIC = fit_results.loc[fit_results.AIC == fit_results.AIC.min()]
best_param = best_AIC['param'].values[0]
best_param_seasonal = best_AIC['param_seasonal'].values[0]

mod = sm.tsa.statespace.SARIMAX(y,
                                order=best_param,
                                seasonal_order=best_param_seasonal,
                                enforce_stationarity=False,
                                enforce_invertibility=False)
results = mod.fit()
print(results.summary().tables[1])

results.plot_diagnostics(figsize=(16, 8))
plt.show()


pred = results.get_prediction(start=pd.to_datetime('2010-01-01'), dynamic=False)
pred_ci = pred.conf_int()
ax = y['2000':].plot(label='observed')
pred.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.7, figsize=(14, 7))
ax.fill_between(pred_ci.index,
                pred_ci.iloc[:, 0],
                pred_ci.iloc[:, 1], color='k', alpha=.2)
ax.set_xlabel('Date')
ax.set_ylabel('Furniture Sales')
plt.legend()
plt.show()

y_forecasted = pred.predicted_mean
y_truth = y['2017-01-01':]
mse = ((y_forecasted - y_truth) ** 2).mean()
print('The Mean Squared Error of our forecasts is {}'.format(round(mse, 2)))

print('The Root Mean Squared Error of our forecasts is {}'.format(round(np.sqrt(mse), 2)))

pred_uc = results.get_forecast(steps=100)
pred_ci = pred_uc.conf_int()
ax = y.plot(label='observed', figsize=(14, 7))
pred_uc.predicted_mean.plot(ax=ax, label='Forecast')
ax.fill_between(pred_ci.index,
                pred_ci.iloc[:, 0],
                pred_ci.iloc[:, 1], color='k', alpha=.25)
ax.set_xlabel('Date')
ax.set_ylabel('Furniture Sales')
plt.legend()
plt.show()
