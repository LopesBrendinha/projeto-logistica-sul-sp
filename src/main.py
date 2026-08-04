from graph.loader import carregar_grafo
from graph.filters import filtrar_nos, filtrar_adjacencia
from graph.components import encontrar_componentes
from graph.random_nodes import selecionar_dois_nos
from visualization.plot_graph import plotar_componente


def main():
    # ==========================
    # 1. Carregar o grafo
    # ==========================
    caminho = "../data/grafo_adjacencia_enriquecido.json"

    nos, adjacencia = carregar_grafo(caminho)

    print(f"Nós totais: {len(nos)}")
    print(f"Lista de adjacência: {len(adjacencia)}")

    # ==========================
    # 2. Filtrar os estados
    # ==========================
    nos_filtrados = filtrar_nos(nos)
    adj_filtrada = filtrar_adjacencia(adjacencia, nos_filtrados)

    print(f"Nós após filtro: {len(nos_filtrados)}")
    print(f"Adjacências após filtro: {len(adj_filtrada)}")

    # ==========================
    # 3. Encontrar componentes conectados
    # ==========================
    componentes = encontrar_componentes(adj_filtrada)

    print(f"Componentes encontrados: {len(componentes)}")

    # Seleciona o maior componente
    maior_componente = max(componentes, key=len)

    print(f"Maior componente: {len(maior_componente)} nós")

    # ==========================
    # 4. Selecionar dois nós aleatórios
    # ==========================
    origem, destino = selecionar_dois_nos(maior_componente)

    print(f"Nó de origem: {origem}")
    print(f"Nó de destino: {destino}")

    # ==========================
    # 5. Gerar visualização
    # ==========================
    plotar_componente(
        nos=nos_filtrados,
        adjacencia=adj_filtrada,
        componente=maior_componente,
        nome_arquivo="../images/maior_componente.png",
        origem=origem,
        destino=destino
    )


if __name__ == "__main__":
    main()