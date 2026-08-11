import random

from graph.loader import carregar_grafo
from graph.filters import filtrar_nos, filtrar_adjacencia
from graph.components import encontrar_componentes
from graph.random_nodes import selecionar_dois_nos
from visualization.plot_graph import plotar_componente
from algorithms.ucs import ucs


def main():
    random.seed(25)
    # ==========================
    # 1. Carregar o grafo
    # ==========================
    caminho = "/home/jorge/Documentos/HUBIA/Disciplinas/Linguagens_de_programacao/Trabalho_final_lp/projeto-logistica-sul-sp/data/grafo_adjacencia_enriquecido.json"

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

    # ==========================
    # 4. UCS em cada componente
    # ==========================
    maior_componente = max(componentes, key=len)

    for i, componente in enumerate(componentes):
        if len(componente) < 2:
            print(f"\n=== Componente {i} ({len(componente)} nó) === (ignorado)")
            continue

        origem, destino = selecionar_dois_nos(componente)

        print(f"\n=== Componente {i} ({len(componente)} nós) ===")
        print(f"Origem: {origem} | Destino: {destino}")

        resultado = ucs(adj_filtrada, origem, destino)

        if resultado is None:
            print("Nenhum caminho encontrado.")
            continue

        caminho_ids, rodovias, distancia_total, explorados = resultado

        print(f"Caminho: {' -> '.join(caminho_ids)}")
        print(f"Rodovias: {' -> '.join(r if r else '(origem)' for r in rodovias)}")
        print(f"Distância total: {distancia_total:.2f} km")
        print(f"Nós explorados pelo UCS: {explorados}")

        ufs = []
        for no_id in caminho_ids:
            uf = nos_filtrados[no_id]["uf_principal"]
            if not ufs or uf != ufs[-1]:
                ufs.append(uf)
        print(f"Estados percorridos: {' -> '.join(ufs)}")

    # ==========================
    # 5. Visualização do maior componente
    # ==========================
    origem_viz, destino_viz = selecionar_dois_nos(maior_componente)

    plotar_componente(
        nos=nos_filtrados,
        adjacencia=adj_filtrada,
        componente=maior_componente,
        nome_arquivo="/home/jorge/Documentos/HUBIA/Disciplinas/Linguagens_de_programacao/Trabalho_final_lp/projeto-logistica-sul-sp/images/maior_componente.png",
        origem=origem_viz,
        destino=destino_viz
        nos_filtrados,
        adj_filtrada,
        componentes,
        "../images/maior_componente.png",
        origem,
        destino
    )
    plotar_componentes_separados(
        nos_filtrados,
        adj_filtrada,
        componentes,
        "../images/componentes_separados.png"
    )

    


if __name__ == "__main__":
    main()