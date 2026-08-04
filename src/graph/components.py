def encontrar_componentes(adjacencia):
    """
    Encontra todos os componentes conectados do grafo utilizando DFS.

    Parâmetros:
        adjacencia (dict): Lista de adjacência do grafo.

    Retorna:
        list: Lista de componentes, onde cada componente é uma lista de nós.
    """

    visitados = set()
    componentes = []

    for no in adjacencia:

        if no not in visitados:

            componente = []
            pilha = [no]

            while pilha:

                atual = pilha.pop()

                if atual in visitados:
                    continue

                visitados.add(atual)
                componente.append(atual)

                for aresta in adjacencia[atual]:

                    destino = str(aresta["destino"])

                    if destino not in visitados:
                        pilha.append(destino)

            componentes.append(componente)

    return componentes