import networkx as nx
import matplotlib.pyplot as plt


def plotar_componente(
    nos,
    adjacencia,
    componentes,
    nome_arquivo,
    origem=None,
    destino=None,
    caminho=None,
    distancia=None,
):
    """
    Desenha todas as componentes conectadas.
    Cada componente recebe uma cor diferente.
    Os nós de origem e destino são destacados.
    """

    G = nx.Graph()

    posicoes = {}

    # Cores das componentes
    cores_componentes = [
        "blue",
        "red",
        "green",
        "orange",
        "purple",
        "brown",
        "pink",
        "gray",
        "olive",
        "cyan",
        "magenta",
        "gold",
        "lime",
        "coral",
        "turquoise",
        "violet",
        "salmon",
        "teal",
        "navy",
        "crimson",
        "darkgreen",
        "darkorange",
        "indigo",
        "deeppink",
        "darkcyan"
    ]

    # Dicionário para saber a qual componente cada nó pertence
    componente_por_no = {}

    for indice, componente in enumerate(componentes):

        for no in componente:
            componente_por_no[no] = indice

            G.add_node(no)

            posicoes[no] = (
                nos[no]["longitude"],
                nos[no]["latitude"]
            )

    # Adiciona as arestas
    for no in G.nodes():

        for aresta in adjacencia[no]:

            destino_aresta = str(aresta["destino"])

            if destino_aresta in G.nodes():
                G.add_edge(no, destino_aresta)

    # Define a cor de cada nó
    cores_nos = []

    for no in G.nodes():

        indice_componente = componente_por_no[no]

        cor = cores_componentes[
            indice_componente % len(cores_componentes)
        ]

        # Destaca origem
        if no == origem:
            cores_nos.append("black")

        # Destaca destino
        elif no == destino:
            cores_nos.append("yellow")

        else:
            cores_nos.append(cor)

    # Cria a figura
    plt.figure(figsize=(14, 12))

    # Desenha as arestas
    nx.draw_networkx_edges(
        G,
        posicoes,
        width=0.4,
        alpha=0.5
    )

    # Destaca a rota UCS
    if caminho:
        arestas_rota = [
            (caminho[i], caminho[i + 1])
            for i in range(len(caminho) - 1)
        ]
        nx.draw_networkx_edges(
            G,
            posicoes,
            edgelist=arestas_rota,
            width=2.5,
            alpha=0.9,
            edge_color="orange",
        )

    nx.draw_networkx_nodes(
        G,
        posicoes,
        node_size=10,
        node_color=cores_nos
    )

    # Rótulos apenas da origem e destino
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

    if caminho and distancia is not None:
        plt.title(
            f"Rota UCS — {len(caminho)} nós, {distancia:.2f} km"
        )
    else:
        plt.title("Maior componente conectado")

    plt.axis("off")

    plt.savefig(
        nome_arquivo,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"Imagem salva em: {nome_arquivo}")


def plotar_componentes_separados(
    nos,
    adjacencia,
    componentes,
    nome_arquivo
):
    """
    Plota somente as componentes menores,
    excluindo a maior componente.
    Cada componente recebe uma cor diferente.
    """

    # Ordena as componentes da maior para a menor
    componentes_ordenados = sorted(
        componentes,
        key=len,
        reverse=True
    )

    # Remove a maior componente
    componentes_menores = componentes_ordenados[1:]

    cores = [
        "red",
        "blue",
        "green",
        "orange",
        "purple",
        "brown",
        "pink",
        "gray",
        "olive",
        "cyan",
        "magenta",
        "gold",
        "lime",
        "coral",
        "turquoise",
        "violet",
        "salmon",
        "teal",
        "navy",
        "crimson",
        "darkgreen",
        "darkorange",
        "indigo",
        "deeppink",
        "darkcyan"
    ]

    plt.figure(figsize=(16, 12))

    for i, componente in enumerate(componentes_menores):

        G = nx.Graph()

        posicoes = {}

        # Adiciona os nós
        for no in componente:

            G.add_node(no)

            posicoes[no] = (
                nos[no]["longitude"],
                nos[no]["latitude"]
            )

        # Adiciona as conexões
        for origem in componente:

            for aresta in adjacencia[origem]:

                destino = str(aresta["destino"])

                if destino in componente:
                    G.add_edge(origem, destino)

        # Escolhe a cor
        cor = cores[i % len(cores)]

        # Desenha as arestas
        nx.draw_networkx_edges(
            G,
            posicoes,
            width=1.5,
            edge_color=cor
        )

        # Desenha os nós
        nx.draw_networkx_nodes(
            G,
            posicoes,
            node_size=300,
            node_color=cor,
            edgecolors="black"
        )

        # Mostra os IDs dos nós
        nx.draw_networkx_labels(
            G,
            posicoes,
            font_size=8,
            font_color="black"
        )

        # Identificação da componente
        centro_x = sum(
            pos[0] for pos in posicoes.values()
        ) / len(posicoes)

        centro_y = sum(
            pos[1] for pos in posicoes.values()
        ) / len(posicoes)

        numero_componente = i + 2

        plt.text(
            centro_x,
            centro_y + 0.03,
            f"Componente {numero_componente}",
            fontsize=9,
            fontweight="bold",
            ha="center"
        )

    plt.title(
        "Componentes conectadas menores - PR, SC, RS e SP"
    )

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")

    plt.grid(True, alpha=0.2)

    plt.tight_layout()

    plt.savefig(
        nome_arquivo,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Imagem das componentes menores salva em: "
        f"{nome_arquivo}"
    )
