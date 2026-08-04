import json


def carregar_grafo(caminho):
    """
    Carrega o arquivo JSON e retorna:
    - nós
    - lista de adjacência
    """

    with open(caminho, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    nos = dados["nos"]
    adjacencia = dados["adjacencia"]

    return nos, adjacencia
    