"""
Módulo para plotagem simples da rota TSP 
"""

import matplotlib.pyplot as plt
import networkx as nx
from typing import List, Dict

def plotar_rota_tsp_simples(
    rota: List[int],
    nos: Dict[int, Dict],
    adjacencia: Dict[int, List[int]] = None,
    titulo: str = "Rota TSP Otimizada",
    salvar: bool = True,
    caminho_arquivo: str = '/content/rota_tsp.png'
) -> None:
  
    if not rota:
        print("⚠️ Rota vazia, não é possível plotar")
        return

    # Criar grafo
    G = nx.Graph()
    pos = {}

    # Adicionar apenas os nós da rota com coordenadas
    for no_id in rota:
        info = nos.get(no_id, {})
        lat = info.get('latitude')
        lon = info.get('longitude')

        if lat is not None and lon is not None:
            pos[no_id] = (lon, lat)
            G.add_node(no_id)

    if not pos:
        print("⚠️ Nenhum nó com coordenadas encontrado")
        return

    # Adicionar arestas da rota (ordem otimizada)
    for i in range(len(rota) - 1):
        if rota[i] in pos and rota[i+1] in pos:
            G.add_edge(rota[i], rota[i+1])

    # Adicionar aresta de volta ao início (rota circular)
    if len(rota) > 1 and rota[-1] in pos and rota[0] in pos:
        G.add_edge(rota[-1], rota[0])

    # Criar figura
    plt.figure(figsize=(12, 10))

    # Definir cores dos nós
    node_colors = []
    node_sizes = []

    for no_id in G.nodes():
        if no_id == rota[0]:  # Ponto inicial
            node_colors.append('green')
            node_sizes.append(300)
        elif no_id == rota[-1]:  # Ponto final
            node_colors.append('red')
            node_sizes.append(300)
        else:
            node_colors.append('blue')
            node_sizes.append(100)

    # Plotar o grafo
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes,
                          alpha=0.8, edgecolors='black', linewidths=1)

    # Plotar arestas da rota
    nx.draw_networkx_edges(G, pos, width=2, edge_color='blue', alpha=0.7)

    # Destacar aresta de retorno
    if len(rota) > 1 and rota[-1] in pos and rota[0] in pos:
        nx.draw_networkx_edges(G, pos, edgelist=[(rota[-1], rota[0])],
                              width=3, edge_color='green', alpha=0.9, style='dashed')

    # Mostrar apenas o ID do início e fim
    labels = {
        rota[0]: f"INÍCIO\n{rota[0]}",
        rota[-1]: f"FIM\n{rota[-1]}"
    }
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold')

    # Adicionar legenda simples
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D

    legend_elements = [
        Patch(facecolor='green', edgecolor='black', label='Início'),
        Patch(facecolor='red', edgecolor='black', label='Fim'),
        Patch(facecolor='blue', edgecolor='black', label='Pontos visitados'),
        Line2D([0], [0], color='blue', linewidth=2, label='Rota percorrida'),
        Line2D([0], [0], color='green', linewidth=2, linestyle='dashed', label='Retorno ao início')
    ]

    plt.legend(handles=legend_elements, loc='upper right', fontsize=10)

    plt.title(titulo, fontsize=14, fontweight='bold')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True, alpha=0.3)

    # Ajustar limites
    if pos:
        x_values = [coord[0] for coord in pos.values()]
        y_values = [coord[1] for coord in pos.values()]
        margin = 0.05
        x_min, x_max = min(x_values), max(x_values)
        y_min, y_max = min(y_values), max(y_values)
        x_range = x_max - x_min
        y_range = y_max - y_min

        if x_range > 0:
            plt.xlim(x_min - x_range*margin, x_max + x_range*margin)
        if y_range > 0:
            plt.ylim(y_min - y_range*margin, y_max + y_range*margin)

    plt.tight_layout()

    if salvar:
        plt.savefig(caminho_arquivo, dpi=300, bbox_inches='tight')
        print(f"🗺️ Rota TSP salva em: {caminho_arquivo}")

    plt.show()