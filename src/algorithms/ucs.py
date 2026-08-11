import heapq


def ucs(adjacencia, origem, destino):
    """
    Busca de Custo Uniforme (UCS).

    Encontra o caminho de menor custo entre dois nós em um grafo com pesos
    não-negativos, utilizando uma fila de prioridade (min-heap).

    Parâmetros:
        adjacencia (dict): Lista de adjacência onde cada aresta contém
                           "destino" (int) e "distancia_km" (float).
        origem (str): ID do nó de partida.
        destino (str): ID do nó de chegada.

    Retorna:
        tuple (caminho_ids, rodovias, custo_total, explorados) se houver caminho,
        ou None se não houver.
    """

    # Inicializa a heap com (custo, nó_atual, caminho, rodovias)
    heap = [(0.0, origem, [origem], [None])]

    # Armazena o menor custo conhecido para alcançar cada nó
    visitados = {}

    # Contador de nós expandidos (iterações do loop)
    explorados = 0

    # Loop principal: expande nós em ordem crescente de custo acumulado
    while heap:

        # Remove da heap o nó com menor custo (propriedade do min-heap)
        custo, atual, caminho_ids, rodovias = heapq.heappop(heap)
        explorados += 1

        # Teste de objetivo: o primeiro caminho encontrado é o de menor custo
        if atual == destino:
            return caminho_ids, rodovias, custo, explorados

        # Poda: descarta se o nó já foi visitado com custo menor ou igual
        if atual in visitados and visitados[atual] <= custo:
            continue

        # Registra o menor custo para alcançar este nó
        visitados[atual] = custo

        # Ignora nós sem vizinhos na adjacência
        if atual not in adjacencia:
            continue

        # Expande todos os vizinhos do nó atual
        for aresta in adjacencia[atual]:

            # Converte destino (int) para string — chaves da adjacência são strings
            vizinho = str(aresta["destino"])

            # Peso da aresta: distância em quilômetros
            peso = aresta["distancia_km"]
            novo_custo = custo + peso

            # Insere na heap apenas se o caminho for mais barato que o conhecido
            if vizinho not in visitados or novo_custo < visitados[vizinho]:
                heapq.heappush(
                    heap,
                    (
                        novo_custo,
                        vizinho,
                        caminho_ids + [vizinho],
                        rodovias + [aresta["rodovia"]],
                    ),
                )

    # Heap vazia: não há caminho entre origem e destino
    return None
