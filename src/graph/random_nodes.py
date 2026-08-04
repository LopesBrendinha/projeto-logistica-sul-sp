import random


def selecionar_dois_nos(componente):
    """
    Seleciona aleatoriamente dois nós distintos de um componente conectado.

    Parâmetros:
        componente (list): Lista de nós do componente.

    Retorna:
        tuple: (origem, destino)
    """

    if len(componente) < 2:
        raise ValueError("O componente precisa ter pelo menos dois nós.")

    origem, destino = random.sample(componente, 2)

    return origem, destino