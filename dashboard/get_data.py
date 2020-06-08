import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

from .models import Estacao, Parametro

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


def create_model(model_name, parametro):
    estacoes = Estacao.objects.all()
    estacoes.sort()
    n = 1
    e_fail = []
    for e in estacoes:
        print(f"Trying nr {n}: {e}")
        e_id = e.est_id
        df, result = get_data(e_id, parametro)
        n += 1
        if result:
            print(df.head())
        else:
            e_fail.append(e)
            continue
        df["est"] = e
        df.columns = [f.name for f in model_name._meta.get_fields()][1:]
        if model_name.objects.filter(est=e).exists():
            model_name.objects.filter(est=e).delete()
        model_name.objects.bulk_create(
            model_name(**vals) for vals in df.to_dict("records")
        )

    e_suc = [e for e in estacoes if e not in e_fail]

    e_suc.sort()
    e_fail.sort()

    if len(e_fail) > 0:
        print(
            f"---SUCCESSS---  {len(e_suc)} estações com sucesso no download/update: {e_suc}"
        )
        print(f"---FAIL---   {len(e_fail)} estações com erro/sem dados: {e_fail}")

    if e_suc == estacoes or len(e_suc) == len(estacoes):
        print(f"Todas as estacoes com sucesso: {n} estacoes")
