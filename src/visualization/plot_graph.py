import networkx as nx
import matplotlib.pyplot as plt


def plotar_componente(
    nos,
    adjacencia,
    componente,
    nome_arquivo,
    origem=None,
    destino=None
):
    """
    Desenha um componente conectado e destaca os nós de origem e destino.
    """

    G = nx.Graph()

    posicoes = {}

    # Adiciona os nós
    for no in componente:
        G.add_node(no)
        posicoes[no] = (
            nos[no]["longitude"],
            nos[no]["latitude"]
        )

    # Adiciona as arestas
    for no in componente:

        for aresta in adjacencia[no]:

            vizinho = str(aresta["destino"])

            if vizinho in componente:
                G.add_edge(no, vizinho)

    # Define as cores dos nós
    cores = []

    for no in G.nodes():

        if no == origem:
            cores.append("green")      # Nó inicial

        elif no == destino:
            cores.append("red")        # Nó final

        else:
            cores.append("skyblue")    # Demais nós

    plt.figure(figsize=(12, 10))

    nx.draw_networkx_edges(
        G,
        posicoes,
        width=0.4,
        alpha=0.5
    )

    nx.draw_networkx_nodes(
        G,
        posicoes,
        node_size=10,
        node_color=cores
    )

    # Exibe apenas os rótulos da origem e do destino
    labels = {}

    if origem is not None:
        labels[origem] = f"O ({origem})"

    if destino is not None:
        labels[destino] = f"D ({destino})"

    nx.draw_networkx_labels(
        G,
        posicoes,
        labels,
        font_size=8
    )

    plt.title("Maior componente conectado")

    plt.axis("off")

    plt.savefig(nome_arquivo, dpi=300)

    plt.close()

    print(f"Imagem salva em: {nome_arquivo}")