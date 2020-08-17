import pandas as pd
from .models import Estacao, Parametro, EstacaoParamUnits
from .get_data import get_data, get_model_from_parameter


# def get_model_from_string(name):
#     name = name.lower()
#     if name in ['mensal', 'precipitacaomensal', 'precipitaçãomensal', 'precipitacao_mensal', 'precipitação_mensal']:
#         return PrecipitacaoMensal
#     elif name in ['diaria', 'diario', 'precipitacaodiaria', 'precipitaçãodiária', 'precipitacao_diaria', 'precipitação_diária']:
#         return PrecipitacaoDiaria
#     else:
#         raise ValueError


def create_model(param_slug=None, param_id=None, replace=True):
    """Populate specific model with data from all estacoes, for specific parametro


    Args:
        model_name (string): name of the model in string, the closest you can get. It will search for such model in our .models.py
        parametro (string): "slug" field of table dashboard_parametros
    """
    try:
        if param_slug:
            qs_p = Parametro.objects.get(slug=param_slug)
        elif param_id:
            qs_p = Parametro.objects.get(param_id=param_id)
        else:
            raise ValueError
    except ValueError:
        print(f"can't find such parameter. Try a different one!")
        return

    try:
        selected_model = get_model_from_parameter(qs_p.param_id)
    except ValueError:
        print(f"can't find such model. Try a different one!")
        return

    if not qs_p:
        print(f"can't find such parameter. Try a different one!")
        return

    estacoes = Estacao.objects.all()

    if not replace:
        estacoes_with_data = selected_model.objects.all().values_list('estacao', flat=True).distinct()
        estacoes = [e for e in estacoes if e.id not in estacoes_with_data]

    n = 1
    e_fail = []
    for e in estacoes:
        print(f"Trying nr {n}: {e}")
        e_id = e.est_id
        df, result = get_data(e_id, qs_p.param_id)
        n += 1
        if result:
            print(df.head())
        else:
            e_fail.append(e)
            continue
        un = df.columns[1].split(' ')[-1].strip('()')

        df["estacao"] = e
        df.columns = ['date', 'value', 'estacao']
        if selected_model.objects.filter(estacao=e).exists():
            selected_model.objects.filter(estacao=e).delete()
        selected_model.objects.bulk_create(
            selected_model(**vals) for vals in df.to_dict("records")
        )
        if EstacaoParamUnits.objects.filter(estacao=e, parametro=qs_p).exists():
            EstacaoParamUnits.objects.filter(estacao=e, parametro=qs_p).delete()
        EstacaoParamUnits.objects.create(
            estacao=e,
            parametro=qs_p,
            un=un
        ).save()

    e_suc = [e for e in estacoes if e not in e_fail]

    # e_suc.sort()
    # e_fail.sort()

    if len(e_fail) > 0:
        e_suc_name = [e.nome for e in e_suc]
        e_fail_name = [e.nome for e in e_fail]

        print(
            f"---SUCCESSS---  {len(e_suc)} estações com sucesso no download/update: {', '.join(e_suc_name)}"
        )
        print(f"---FAIL---   {len(e_fail)} estações com erro/sem dados:  {', '.join(e_fail_name)}")

    if e_suc == estacoes or len(e_suc) == len(estacoes):
        print(f"Todas as estacoes com sucesso: {n} estacoes")


# Parametro.objects.create(
#     param_id=1041803938,
#     designacao="Velocidade do vento instatânea",
#     freq=None,
# ).save()
