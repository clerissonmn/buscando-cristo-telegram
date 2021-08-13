from datetime import datetime as dt
from io import BytesIO

import pandas as pd
import requests
from pandas.io.parsers import read_csv


def baixa_csv_do_gsheets(doc_key=None, sheet_name=None, verbose=False, to_file=None):
    """Baixa o csv a partir de uma planilha pública do google sheets.

    Args:
        doc_key ([type], optional): [description]. Defaults to None.
        sheet_name ([type], optional): [description]. Defaults to None.
        verbose (bool, optional): [description]. Defaults to False.
        to_file ([type], optional): [description]. Defaults to None.

    Returns:
        <class '_io.BytesIO'>: csv en formato binário.
    """

    raw_link = f"https://docs.google.com/spreadsheets/d/{doc_key}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

    _vprint(verbose, "Link:", raw_link)

    response = requests.get(raw_link)

    assert (
        response.status_code == 200
    ), f"Erro ao acessar a planilha. Erro = {response.status_code}"

    raw_csv = BytesIO(response.content)

    if to_file:
        try:
            with open("tabela.csv", "wb") as arquivo:
                arquivo.write(raw_csv.getbuffer())
        except:
            return f"Arquivo não foi criado corretamente."

    return raw_csv


def carrega_segredos(file=None, verbose=False):
    """Parse que cria um dict no formato {chave : valor} a partir
    do arquivo contendo os segredos no formato chave = valor.

    Args:
        file (string, obrigatório): Arquivo contendo as palavras secretas.
        verbse (bool, opcional): True printa as mensagens de debug.

    Returns:
        dict: dicionário no formato {chave : valor}
    """

    segredos = dict()
    for linha in open(file).readlines():

        key, value = linha.split("=")

        # Sanitize string
        saitizar = "'\" \n"
        key = key.strip(saitizar)
        value = value.strip(saitizar)

        _vprint(verbose, f"string sanitizada: {key}:{value}")

        segredos.update({key: value})

    _vprint(verbose, f"As chaves disponíveis são: {[i for i in segredos.keys()]}")

    return segredos


def _vprint(verbose, *args, **kwargs):
    if verbose:
        print("==>", *args, **kwargs)


_dias_da_semana = {
    "Monday": "Segunda-feira",
    "Tuesday": "Terça-feira",
    "Wednesday": "Quarta-feira",
    "Thursday": "Quinta-feira",
    "Friday": "Sexta-feira",
    "Saturday": "Sábado",
    "Sunday": "Domingo",
}

hoje = _dias_da_semana[dt.today().strftime("%A")]


def traduz(dia_em_ingles, traducao=_dias_da_semana):
    """Pega um dia da semana em inglês e traduz para pt-BR

    Args:
        dia_em_ingles (str): Dia da semana em inglês.
        traducao (dict): Dicionário contedo a tradução dos dias da semana.

    Returns:
        str: Dia da semana em pt-BR mas sem \"-feira\"
    """

    return traducao[dia_em_ingles].split("-")[0]


def pega_horarios(
    df,
    programacao=None,
    natureza=None,
    cidade=None,
    bairro=None,
    dia_da_semana="hoje",
    formato_saida="dataframe",
):
    """Função que retorna os horários do evento para os dias da semana escolhidos."""

    dias = [traduz(dt.today().strftime("%A")).split("-")[0]]

    colunas = [
        "Natureza",
        "Programação",
        "Local",
        "Endereço",
        "Bairro",
        "Cidade",
        "Contato",
    ] + dias

    query = ""

    if programacao:
        query += f"'{programacao}' in Programação"

        if natureza:
            query += f" and '{natureza}' in Natureza"

        if cidade != "todas":
            if cidade.lower() not in ["belém", "ananindeua", "todas"]:
                return f"{cidade} inválida. Valores permitidos são Belém e Ananindeua."
            query += f" and '{cidade}' in Cidade"

    df = (
        df[colunas]
        .query(query)  # Aplica a busca
        .dropna(axis=1, how="all")  # Tira as colunas onde tudo é na
        .dropna(axis=0, subset=dias)  # Tira apenas as linhas onde o dia da semana é na
        .reset_index(drop=True)
        .rename(columns={dias[0]: "Horários"})
    )

    if formato_saida == "dict":
        return df.to_dict()

    return df


def formata_mensagem(
    resultado=None, cidade=None, natureza=None, programacao=None, dia=None
):
    mensagem = f"""  == {hoje} ==

#{programacao} em #{cidade}:
"""

    for i in resultado["Programação"].keys():
        mensagem += f"""
**{resultado['Local'][i]} ({resultado['Contato'][i]})**
**Horários:** {resultado['Horários'][i]}
**Endereço:** {resultado['Endereço'][i]} ({resultado['Bairro'][i]})
"""

    return mensagem


def mensagem_formatada(dia=None, doc_key=None, sheet_name=None):

    tabela_csv = baixa_csv_do_gsheets(doc_key=doc_key, sheet_name=sheet_name)
    df = read_csv(tabela_csv)

    if dia:
        dia_da_semana = dia.capitalize()
    else:
        dia_da_semana = hoje

    programacao_lista = ["Missa", "Confissão"]
    cidade_lista = ["Belém", "Ananindeua"]

    mensagens = list()
    for programacao in programacao_lista:
        for cidade in cidade_lista:
            print(f"==> Enviando {programacao} em {cidade} para {dia_da_semana}")

            resultado = pega_horarios(
                df=df,
                programacao=programacao,
                natureza="Presencial",
                cidade=cidade,
                bairro="todos",
                dia_da_semana=dia_da_semana,
                formato_saida="dict",
            )

            # Formata em uma mensagem
            mensagem = formata_mensagem(
                resultado=resultado,
                cidade=cidade,
                programacao=programacao,
                dia=dia_da_semana,
            )

            mensagens.append(mensagem)

    return mensagens
