import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

from .models import Estacao, Parametro, PrecipitacaoMensal, PrecipitacaoDiaria

# Mangualde
# estacao = 920685448

# mensal
# parametro = 1436794570

# horario
# parametro = 100744007


def get_data(estacao=920685448, parametro=1436794570, date_begin=datetime(1930, 1, 1), date_end=datetime.now()):
    """
  {'Precipitação anual': 4237, 'Precipitação diária máxima anual': 1578135698, 'Precipitação mensal': 1436794570,
  'Direcção do vento horária': 1857, 'Precipitação diária': 413026594, 'Precipitação horária': 100744007,
  'Velocidade do vento horária': 100750606, 'Velocidade do vento máxima horária': 100750612,
  'Velocidade do vento média diária': 490270858, 'Velocidade do vento instantânea': 1041803938}

  date_begin: format datetime, dd-mm-YYYY or dd/mm/YYYY
  date_end: format datetime, dd-mm-YYYY or dd/mm/YYYY
  """
    print(f'a reunir dados para estacao {estacao} e parametro {parametro}...')
    if isinstance(date_begin, datetime):
        date_begin_f = date_begin.strftime("%d/%m/%Y")
    elif "-" in date_begin:
        date_begin_f = date_begin.replace("-", "/")

    if isinstance(date_end, datetime):
        date_end_f = date_end.strftime("%d/%m/%Y")
    elif "-" in date_end:
        date_end_f = date_end.replace("-", "/")

    url = f"https://snirh.apambiente.pt/snirh/_dadosbase/site/janela_verdados.php?sites={estacao}&pars={parametro}&tmin={date_begin_f}&tmax={date_end_f}"

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        tbl = soup.find("table", {"align": "center"}, "tbody").find("table")

        # df = pd.DataFrame(columns=['Data', 'p'])

        # with open("index.csv", 'w', newline='') as csv_file:
        #     writer = csv.writer(csv_file)
        #     for trs in tbl.find_all('tr')[2:]:
        #         tds = trs.find_all('td')
        #         row = [elem.text.strip() for elem in tds]
        #         print(row)
        #         writer.writerow(row)
        try:
            df = pd.read_html(str(tbl), skiprows=1)[0]
        except ValueError:
            print("-sem tabela")
            return None, False
        df.columns = df.iloc[0, :]
        df.drop(0, inplace=True)
        df.Data = pd.to_datetime(df.Data, format="%d/%m/%Y %H:%M")
        return df, True
    except:
        return None, False


def all_stations_month_data():
    df_total = pd.DataFrame()
    all_meteo_stations = Estacao.objects.filter(rede__slug='meteorologica')
    for estacao in all_meteo_stations:
        df, result = get_data(estacao=estacao.est_id, parametro=1436794570)
        if not result:
            continue
        print('--success!')
        df['estacao'] = estacao.est_id
        df_total = df_total.append(df)

    # df_total.to_csv('monthly_rainfall.csv')
    return df_total


def update_timeseries(estacao=920685448, parametro=1436794570, date_begin=datetime(1930, 1, 1), date_end=datetime.now(), replace=True):
    from .models import Estacao, Parametro, AnyTimeseriesData
    df, result = get_data(estacao, parametro, date_begin, date_end)
    if result:
        df.columns = ['date', 'value']
        estacao_obj = Estacao.objects.get(est_id=estacao)
        parametro_obj = Parametro.objects.get(param_id=parametro)

        df['estacao'] = estacao_obj
        df['parametro'] = parametro_obj

        if replace:
            AnyTimeseriesData.objects.filter(
                estacao=estacao_obj,
                parametro=parametro_obj,
                date__in=df.date.tolist()
            ).delete()
        else:
            qs = AnyTimeseriesData.objects.filter(
                estacao=estacao_obj,
                parametro=parametro_obj,
                date__in=df.date.tolist()
            )
            existing_dates = qs.values_list('date', flat=True)
            df = df.loc[~df.date.isin(existing_dates)]

        print('A atualizar AnyTimeseriesData...')
        AnyTimeseriesData.objects.bulk_create(AnyTimeseriesData(**vals) for vals in df.to_dict("records"))
        print('Done!\n')


def update_timeseries_rede(rede_txt, date_begin=datetime(2010, 1, 1), date_end=datetime.now(), replace=True):
    from .models import Rede, ParametroUnit
    from django.utils.text import slugify

    try:
        rede_obj = Rede.objects.get(slug=slugify(rede_txt))
    except:
        print(f'Rede {rede_txt} não identificada!')
        return

    print(f'A atualizar base de dados para a rede {rede_txt}')

    estacoes_parametros = ParametroUnit.objects.filter(estacao__rede=rede_obj)
    for est_param in estacoes_parametros:
        update_timeseries(estacao=est_param.estacao.est_id, parametro=est_param.parametro.param_id,
                          date_begin=date_begin, date_end=date_end, replace=replace)
