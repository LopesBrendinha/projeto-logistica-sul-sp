import random
import networkx as nx
from graph.loader import carregar_grafo
from graph.filters import filtrar_nos, filtrar_adjacencia
from graph.components import encontrar_componentes
from graph.random_nodes import selecionar_dois_nos
from visualization.plot_graph import plotar_componente, plotar_componentes_separados
from algorithms.ucs import ucs
from graph import informacoes_pontos
from algorithms.tsp import executar_tsp_com_pontos
from graph.otimizador_rotas import otimizar_rota_2opt
from visualization.plotagem_tsp import plotar_rota_tsp_simples


def main():
    random.seed(25)
    # ==========================
    # 1. Carregar o grafo
    # ==========================
    caminho = "/home/maria-vit-ria-nogueira-de-souza/Documentos/IA_M1/projeto-logistica-sul-sp/data/grafo_adjacencia_enriquecido.json"

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

        if componente is maior_componente:
            maior_caminho = caminho_ids
            maior_origem = origem
            maior_destino = destino
            maior_distancia = distancia_total

    # ==========================
    # 5. Visualização da rota UCS no maior componente
    # ==========================
    plotar_componente(
        nos=nos_filtrados,
        adjacencia=adj_filtrada,
        componentes=[maior_componente],
        nome_arquivo="/home/jorge/Documentos/HUBIA/Disciplinas/Linguagens_de_programacao/Trabalho_final_lp/projeto-logistica-sul-sp/images/ucs_result.png",
        origem=maior_origem,
        destino=maior_destino,
        caminho=maior_caminho,
        distancia=maior_distancia,
    )

    # ==========================
    # 6. Visualização das componentes menores
    # ==========================
    plotar_componentes_separados(
        nos_filtrados,
        adj_filtrada,
        componentes,
        "/home/maria-vit-ria-nogueira-de-souza/Documentos/IA_M1/projeto-logistica-sul-sp/images/componentes_separados.png"
    )

    # ==========================
    # 4. TSP (Algoritmo Genético)
    # ==========================

    # Seleção de pontos por UF para o TSP (Estado escolhido foi o de São Paulo (SP))
    pontos_sp = [no for no in maior_componente
                 if nos_filtrados.get(no, {}).get('uf_principal') == 'SP']

    print(f"\n📌 Pontos no estado de SP: {len(pontos_sp)}")

    # Verificar se encontrou pontos em SP
    if len(pontos_sp) == 0:
        print("⚠️ Nenhum ponto encontrado para SP. Usando pontos aleatórios.")
        # Fallback: usar pontos aleatórios
        num_pontos_tsp = min(45, len(maior_componente))
        pontos_selecionados = random.sample(maior_componente, num_pontos_tsp)
    else:
        # Selecionar até 30 pontos de SP
        num_pontos_tsp = min(45, len(pontos_sp))
        pontos_selecionados = random.sample(pontos_sp, num_pontos_tsp)

    print(f"Pontos selecionados para o TSP: {len(pontos_selecionados)}")
    print(f"IDs: {pontos_selecionados[:10]}{'...' if len(pontos_selecionados) > 10 else ''}")

    # Mostrar informações dos pontos selecionados
    print("\n📋 Pontos selecionados:")
    for i, no_id in enumerate(pontos_selecionados[:5], 1):
        info = nos_filtrados.get(no_id, {})
        uf = info.get('uf_principal', 'N/A')
        regiao = info.get('regiao_principal', 'N/A')
        lat = info.get('latitude', 'N/A')
        lon = info.get('longitude', 'N/A')
        print(f"   {i}. ID: {no_id} | UF: {uf} | Região: {regiao} | Coord: ({lat}, {lon})")


    # Algoritmo Genético - TSP
    print("\n" + "="*60)
    print("ALGORITMO GENÉTICO PARA TSP")
    print("="*60)

    # Executar o algoritmo genético com os pontos selecionados
    resultado_tsp = executar_tsp_com_pontos(
        pontos=pontos_selecionados,
        adjacencia=adj_filtrada,
        nos=nos_filtrados,
        populacao_tamanho=100,    # Tamanho da população
        geracoes=100,             # Número de gerações
        taxa_mutacao=0.1,         # Taxa de mutação
        taxa_cruzamento=0.8,      # Taxa de cruzamento
        elitismo=2,               # Elitismo
        verbose=True              # Mostrar progresso
    )

    # ================================================================
    # OTIMIZAÇÃO 2-OPT - ELIMINAR CRUZAMENTOS
    # ================================================================
    # from otimizador_rotas import otimizar_rota_2opt

    print("\n" + "="*60)
    print("OTIMIZAÇÃO DA ROTA COM 2-OPT")
    print("="*60)

    # Otimizar a rota encontrada pelo AG
    resultado_otimizacao = otimizar_rota_2opt(
        rota=resultado_tsp['rota'],
        nos=nos_filtrados,
        verbose=True
    )

    # Atualizar com a rota otimizada
    rota_otimizada = resultado_otimizacao['rota_otimizada']
    distancia_total = resultado_otimizacao['distancia_otimizada']

    # ================================================================
    # EXIBIR RESULTADOS DO TSP
    # ================================================================
    print("\n" + "="*60)
    print("RESULTADO DO TSP")
    print("="*60)

    print(f"\n✅ Melhor rota encontrada:")
    print(f"   Distância total: {distancia_total:.2f} km")
    print(f"   Número de pontos: {len(rota_otimizada)}")
    print(f"   Cruzamentos na rota: {resultado_otimizacao['cruzamentos_otimizada']}")
    print(f"   Cruzamentos eliminados: {resultado_otimizacao['cruzamentos_eliminados']}")
    print(f"   Melhoria 2-opt: {resultado_otimizacao['melhoria_percentual']:.2f}%")

    print(f"\n   📊 COMPARAÇÃO:")
    print(f"   Distância AG: {resultado_tsp['distancia']:.2f} km")
    print(f"   Distância após 2-opt: {distancia_total:.2f} km")
    print(f"   Melhoria total: {resultado_tsp['distancia'] - distancia_total:.2f} km ({((resultado_tsp['distancia'] - distancia_total) / resultado_tsp['distancia'] * 100):.1f}%)")

    print(f"\n🗺️ Rota otimizada (IDs):")
    for i, no_id in enumerate(rota_otimizada, 1):
        info = nos_filtrados.get(no_id, {})
        uf = info.get('uf_principal', 'N/A')
        regiao = info.get('regiao_principal', 'N/A')
        lat = info.get('latitude', 'N/A')
        lon = info.get('longitude', 'N/A')
        print(f"   {i:2d}. ID: {str(no_id):>6s} | UF: {str(uf):2s} | Região: {str(regiao):12s} | Coord: ({lat}, {lon})")

    # Salvar rota em arquivo
    with open('/home/maria-vit-ria-nogueira-de-souza/Documentos/IA_M1/projeto-logistica-sul-sp/results/rota_otimizada_tsp_sp.txt', 'w', encoding='utf-8') as f:
        f.write("ROTA OTIMIZADA - TSP (SP) COM 2-OPT\n")
        f.write("="*80 + "\n")
        f.write(f"Distância total: {distancia_total:.2f} km\n")
        f.write(f"Número de pontos: {len(rota_otimizada)}\n")
        f.write(f"Cruzamentos eliminados: {resultado_otimizacao['cruzamentos_eliminados']}\n")
        f.write("-"*80 + "\n")
        f.write("Posição | ID     | UF   | Região         | Latitude  | Longitude\n")
        f.write("-"*80 + "\n")

        for i, no_id in enumerate(rota_otimizada, 1):
            info = nos_filtrados.get(no_id, {})
            uf = info.get('uf_principal', 'N/A')
            regiao = info.get('regiao_principal', 'N/A')
            lat = info.get('latitude', 'N/A')
            lon = info.get('longitude', 'N/A')
            f.write(f"{i:6d} | {str(no_id):>6s} | {str(uf):5s} | {str(regiao):14s} | {str(lat):10s} | {str(lon):10s}\n")

    print(f"\n💾 Rota salva em: /content/rota_otimizada_tsp_sp.txt")


    # ================================================================
    # PLOTAGEM SIMPLES DA ROTA TSP
    # ================================================================

    print("\n" + "="*60)
    print("PLOTANDO ROTA TSP")
    print("="*60)

    # Plotar a rota otimizada sobre o grafo
    plotar_rota_tsp_simples(
        rota=resultado_tsp['rota'],
        nos=nos_filtrados,
        adjacencia=adj_filtrada,
        titulo=f"Rota TSP Otimizada - SP ({len(resultado_tsp['rota'])} pontos, {resultado_tsp['distancia']:.2f} km)",
        salvar=True,
        caminho_arquivo='/home/maria-vit-ria-nogueira-de-souza/Documentos/IA_M1/projeto-logistica-sul-sp/images/rota_tsp_sp.png'
    )
if __name__ == "__main__":
    main()