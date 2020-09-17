from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import InvalidElementStateException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import unidecode
import pandas as pd
from bs4 import BeautifulSoup
from dashboard.models import *
from seed_db.seed_db import df_to_estacao, df_to_hidro
from django.utils.text import slugify
import time
estacao_columns = ['codigo', 'nome', 'altitude', 'latitude', 'longitude', 'coord_x', 'coord_y', 'responsavel_aut',
                   'responsavel_con', 'estacao_con', 'estacao_aut', 'entrada_con', 'encerra_con', 'entrada_aut', 'encerra_aut', 'est_id']
hidro_columns = ['area_drenada', 'cota_escala', 'rio', 'est_id']
rename_cols = {
    "código": "codigo",
    "nome_x": "nome",
    "altitude (m)": "altitude",
    "latitude (on)": "latitude",
    "longitude (ow)": "longitude",
    "coord_x (m)": "coord_x",
    "coord_y (m)": "coord_y",
    "area drenada (km2)": "area_drenada",
    "cota zero escala (m)": "cota_escala",
    "entidade responsavel (automatica)": "responsavel_aut",
    "entidade responsavel (convencional)": "responsavel_con",
    "tipo estacao (convencional)": "estacao_con",
    "tipo estacao (automatica)": "estacao_aut",
    "entrada funcionamento (convencional)": "entrada_con",
    "encerramento (convencional)": "encerra_con",
    "entrada funcionamento (automatica)": "entrada_aut",
    "encerramento (automatica)": "encerra_aut",
    "val": "est_id"
}


def regular_driver():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    # prefs = {"download.default_directory": downloads_path}
    # chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome("chromedriver.exe", options=chrome_options)
    return driver


def conect_driver(website):
    driver = regular_driver()
    driver.get(website)  # Inicio do website pretendido no webdriver
    action = ActionChains(driver)
    global wait
    global wait_long
    wait_short = WebDriverWait(driver, 10)
    wait = WebDriverWait(driver, 30)
    wait_long = WebDriverWait(driver, 100)
    return driver, action, wait, wait_long, wait_short


def get_redes_info():
    driver, action, wait, wait_long, wait_short = conect_driver(
        'https://snirh.apambiente.pt/index.php?idMain=2&idItem=1')
    driver.execute_script("javascript:DBASE_MostraDivFiltro('REDES')")

    rede_select = wait.until(ec.presence_of_element_located((By.XPATH, "//select[@name='f_redes_todas[]']")))
    rede_options = rede_select.find_elements_by_tag_name('option')
    df_dic = [{'rede_id': r.get_attribute('value'), 'nome': r.text} for r in rede_options]
    df = pd.DataFrame().from_dict(df_dic)
    driver.close()
    Rede.objects.all().delete()
    for i, r in df.iterrows():
        Rede(
            rede_id=r.rede_id,
            nome=r.nome
        ).save()
    # Rede.objects.bulk_create(Rede(**vals) for vals in df.to_dict("records"))


def read_table_html(driver, table_id):
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table_h = soup.find("table", {'id': table_id})
    df = pd.read_html(str(table_h))[0]
    df.columns = [unidecode.unidecode(d).lower() for d in df.columns]
    return df


def split_estacao_codigo(x):
    try:
        x_spl = x.split(' ')
        codigo = x_spl[-1].strip('()')
        # name = (' ').join(x_spl[:-1])
        return codigo
    except:
        return x


def split_estacao_name(x):
    try:
        x_spl = x.split(' ')
        # codigo = x_spl[-1].strip('()')
        name = (' ').join(x_spl[:-1])
        return name
    except:
        return x


def get_estacao_from_codigo(codigo):
    try:
        return Estacao.objects.get(codigo=codigo)
    except:
        print(f"cant find {codigo} in stations codigos")


def get_parametro_from_designacao(designacao):
    return Parametro.objects.get(slug=slugify(designacao))


def dump_params(df_parametros_base, df_parametros_units, replace):
    if replace:
        Parametro.objects.filter(param_id__in=df_parametros_base.param_id.tolist()).delete()
    else:
        param_id_saved = Parametro.objects.values_list('param_id', flat=True)
        df_parametros_base = df_parametros_base.loc[~df_parametros_base.param_id.isin(param_id_saved)]
    for i, r in df_parametros_base.iterrows():
        Parametro(
            param_id=r.param_id,
            designacao=r.designacao
        ).save()
    df_parametros_units['codigo'] = df_parametros_units.estacao.map(split_estacao_codigo)
    df_parametros_units['nome'] = df_parametros_units.estacao.map(split_estacao_name)
    df_parametros_units['estacao'] = df_parametros_units.codigo.map(get_estacao_from_codigo)
    df_parametros_units['parametro'] = df_parametros_units.parametro.map(get_parametro_from_designacao)
    df_parametros_units['data_inicio'] = pd.to_datetime(df_parametros_units['data inicio'])
    df_parametros_units['data_fim'] = pd.to_datetime(df_parametros_units['data final'])
    df_parametros_units.rename(columns={'n.o valores': 'numero_valores'}, inplace=True)
    df_parametros_units = df_parametros_units[["parametro", "estacao",
                                               "unidade", "data_inicio", "data_fim", "numero_valores"]]
    df_parametros_units.reset_index(drop=True, inplace=True)
    if replace:
        ParametroUnit.objects.filter(parametro__in=df_parametros_units.parametro.tolist(),
                                     estacao__in=df_parametros_units.estacao.tolist()).delete()
    else:
        for i, r in df_parametros_units.iterrows():
            print(i)
            qs = ParametroUnit.objects.filter(estacao=r.estacao, parametro=r.parametro)
            if qs:
                df_parametros_units.drop(i, inplace=True)
    ParametroUnit.objects.bulk_create(ParametroUnit(**vals) for vals in df_parametros_units.to_dict("records"))


def gather_params(rede_txt, replace=True):
    # rede_txt = 'meteorologica'
    # get_params = True
    # replace = True
    driver, action, wait, wait_long, wait_short = conect_driver(
        'https://snirh.apambiente.pt/index.php?idMain=2&idItem=1')

    driver.execute_script("javascript:DBASE_MostraDivFiltro('REDES')")
    rede_select = wait.until(ec.presence_of_element_located((By.XPATH, "//select[@name='f_redes_todas[]']")))
    rede_options = rede_select.find_elements_by_tag_name('option')
    # clean_rede_txt = unidecode.unidecode(rede_txt).lower()

    for r in rede_options:
        if unidecode.unidecode(r.text).lower() == unidecode.unidecode(rede_txt).lower():
            action.double_click(r).perform()
            break

    wait.until(ec.presence_of_element_located(
        (By.XPATH, "//input[@id='bf_filtro_aplicar' and @value='Aplicar Filtros']"))).click()

    select_el = wait.until(ec.presence_of_element_located((By.XPATH, "//select[@id='f_estacoes[]']")))

    df_parametros_base = pd.DataFrame(columns=['param_id', 'designacao'])
    df_parametros_units = pd.DataFrame()
    all_options = select_el.find_elements_by_tag_name('option')
    all_options_val = [op.get_attribute('value') for op in all_options]
    for op_val in all_options_val:
        # op_val = all_options_val[1]
        df_parametros_dump = pd.DataFrame(columns=['param_id', 'designacao'])
        print(f"--getting params of station {op_val}")
        wait.until(ec.presence_of_element_located(
            (By.XPATH, f"//option[@value='{op_val}']"))).click()
        driver.execute_script("DBASE_SeleccionaEstacoesDaLista();")
        wait.until(ec.presence_of_element_located((By.ID, "bt_validarlista"))).click()
        select_p = wait.until(ec.presence_of_element_located((By.XPATH, "//select[@id='f_estacoes_parametros[]']")))
        all_parameters = select_p.find_elements_by_tag_name('option')
        print(f"---getting params base")
        for p in all_parameters:
            # p = all_parameters[0]
            param_id = p.get_attribute('value')
            designacao = p.text[2:]
            if param_id in df_parametros_base.param_id.unique():
                continue

            df_parametros_base.loc[len(df_parametros_base)] = [param_id, designacao]
            df_parametros_dump.loc[len(df_parametros_dump)] = [param_id, designacao]
        print(f"---getting params units")
        driver.get("https://snirh.apambiente.pt/snirh/_dadosbase/site/janela.php?obj_janela=INFO_PARAMETROS&tp_lista=I")
        df_parametros_units = read_table_html(driver, 'DBASE_TabelaInfoParametros')

        print(f"---Dumping Data")
        try:
            dump_params(df_parametros_dump, df_parametros_units, replace)
        except Exception as e:
            print(f"\nSomething went wrong with dumping parameter {op_val}: {e}\n")
            return
        driver.get('https://snirh.apambiente.pt/index.php?idMain=2&idItem=1')
        wait.until(ec.presence_of_element_located((By.ID, "bt_limparlista"))).click()
        print(f"----DONE!")
    driver.close()


def get_station_info(rede_txt, get_params=True, replace=True):
    # rede_txt = 'hidrometrica'
    # get_params = True
    # replace = True

    try:
        rede_obj = Rede.objects.get(slug=slugify(rede_txt))
    except:
        print(f'Rede {rede_txt} não identificada!')
        return
    print(f'\n\nTrying {rede_txt}...')

    driver, action, wait, wait_long, wait_short = conect_driver(
        'https://snirh.apambiente.pt/index.php?idMain=2&idItem=1')

    driver.execute_script("javascript:DBASE_MostraDivFiltro('REDES')")
    rede_select = wait.until(ec.presence_of_element_located((By.XPATH, "//select[@name='f_redes_todas[]']")))
    rede_options = rede_select.find_elements_by_tag_name('option')
    # clean_rede_txt = unidecode.unidecode(rede_txt).lower()

    for r in rede_options:
        if unidecode.unidecode(r.text).lower() == unidecode.unidecode(rede_txt).lower():
            action.double_click(r).perform()
            break

    wait.until(ec.presence_of_element_located(
        (By.XPATH, "//input[@id='bf_filtro_aplicar' and @value='Aplicar Filtros']"))).click()

    select_el = wait.until(ec.presence_of_element_located((By.XPATH, "//select[@id='f_estacoes[]']")))

    df_id = pd.DataFrame(columns=['est_id', 'codigo', 'nome'])

    all_options = select_el.find_elements_by_tag_name('option')
    all_options_val = [op.get_attribute('value') for op in all_options]

    print(f'goingo for {len(all_options)} insts...')
    for op_val in all_options_val:
        # op_val = all_options_val[0]
        op = wait.until(ec.presence_of_element_located(
            (By.XPATH, f"//option[@value='{op_val}']")))
        txt = op.text[2:]
        print(f"-trying {txt}")
        codigo = split_estacao_codigo(txt)
        name = split_estacao_name(txt)
        df_id.loc[len(df_id)] = [op_val, codigo, name]

    # dump_params(df_parametros_base, df_parametros_units, replace)
    driver.get('https://snirh.apambiente.pt/snirh/_dadosbase/site/janela.php?obj_janela=INFO_ESTACOES')

    df_info = read_table_html(driver, 'DBASE_TabelaInfoEstacoes')
    driver.close()

    df_total = df_info.merge(df_id, left_on='codigo', right_on='codigo')
    df_total.rename(columns=rename_cols, inplace=True)

    df_estacao = df_total[[c for c in estacao_columns if c in df_total.columns]]

    for c in estacao_columns:
        if c not in df_estacao.columns:
            df_estacao[c] = None

    df_estacao['rede'] = rede_obj
    df_to_estacao(df_estacao, replace=replace)

    try:
        df_hidro = df_total[[c for c in hidro_columns if c in df_total.columns]]
        df_hidro_t = df_hidro.drop(columns='est_id')

        if df_hidro_t.empty:
            print(f"-->No hidro data")
        else:
            df_hidro['rede'] = rede_obj
            for c in hidro_columns:
                if c not in df_hidro.columns:
                    df_hidro[c] = None

            df_to_hidro(df_hidro, replace=replace)
    except Exception as e:
        print(f"----->can't really fill hidro: {e}")

    if get_params:
        gather_params(rede_txt, replace)


def update_all():
    for r in Rede.objects.all():
        # get_station_info("meteorologica")
        get_station_info(r.nome)
