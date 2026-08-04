from graph.loader import carregar_grafo
from graph.filters import filtrar_nos, filtrar_adjacencia
from graph.components import encontrar_componentes
from visualization.plot_graph import plotar_componente


def main():

    caminho = "../data/grafo_adjacencia_enriquecido.json"

    # Carrega o grafo
    nos, adjacencia = carregar_grafo(caminho)

    print(f"Nós totais: {len(nos)}")
    print(f"Lista de adjacência: {len(adjacencia)}")

    # Filtra os estados
    nos_filtrados = filtrar_nos(nos)
    adj_filtrada = filtrar_adjacencia(adjacencia, nos_filtrados)

    print(f"Nós após filtro: {len(nos_filtrados)}")
    print(f"Adjacências após filtro: {len(adj_filtrada)}")

    # Encontra os componentes
    componentes = encontrar_componentes(adj_filtrada)

    print(f"Componentes encontrados: {len(componentes)}")

    # Seleciona o maior componente
    maior_componente = max(componentes, key=len)

    print(f"Maior componente: {len(maior_componente)} nós")

    # Gera a imagem
    plotar_componente(
        nos_filtrados,
        adj_filtrada,
        maior_componente,
        "../images/maior_componente.png"
    )


if __name__ == "__main__":
    main()