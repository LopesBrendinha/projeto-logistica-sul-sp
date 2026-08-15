import random
import math
import numpy as np
from typing import List, Tuple, Dict, Optional, Set
from collections import defaultdict
import time

class AlgoritmoGeneticoTSP:
    """
    Implementação do Algoritmo Genético para TSP
    """

    def __init__(
        self,
        adjacencia: Dict[int, List[int]],
        nos: Dict[int, Dict],
        populacao_tamanho: int = 100,
        geracoes: int = 100,
        taxa_mutacao: float = 0.1,
        taxa_cruzamento: float = 0.8,
        elitismo: int = 2,
        seed: Optional[int] = None
    ):
        """
        Inicializa o algoritmo genético para TSP

        Args:
            adjacencia: Dicionário de adjacência do grafo
            nos: Dicionário com informações dos nós
            populacao_tamanho: Tamanho da população
            geracoes: Número de gerações
            taxa_mutacao: Taxa de mutação (0 a 1)
            taxa_cruzamento: Taxa de cruzamento (0 a 1)
            elitismo: Número de melhores indivíduos preservados
            seed: Semente para reproducibilidade
        """
        self.adjacencia = adjacencia
        self.nos = nos
        self.populacao_tamanho = populacao_tamanho
        self.geracoes = geracoes
        self.taxa_mutacao = taxa_mutacao
        self.taxa_cruzamento = taxa_cruzamento
        self.elitismo = elitismo

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        # Cache para distâncias
        self.distancias_cache = {}

        # Melhor solução encontrada
        self.melhor_rota = None
        self.melhor_distancia = float('inf')
        self.historico_melhores = []
        self.historico_medias = []

    ### Funções para o cálculo de distancia (entre pontos = foi utilizado a distância euclidiana) e distância da rota total
    def calcular_distancia(self, no1: int, no2: int) -> float:
        """
        Calcula a distância entre dois nós usando coordenadas geográficas
        """
        # Verificar cache
        key = tuple(sorted([no1, no2]))
        if key in self.distancias_cache:
            return self.distancias_cache[key]

        # Obter coordenadas
        info1 = self.nos.get(no1, {})
        info2 = self.nos.get(no2, {})

        lat1 = info1.get('latitude')
        lon1 = info1.get('longitude')
        lat2 = info2.get('latitude')
        lon2 = info2.get('longitude')

        # Se não tiver coordenadas, usar distância baseada em adjacência
        if lat1 is None or lat2 is None:
            # Distância: 1 se conectado, INF se não
            dist = 1.0 if no2 in self.adjacencia.get(no1, []) else float('inf')
            self.distancias_cache[key] = dist
            return dist

        # Calcular distância euclidiana (em graus decimais)
        # Aproximação: 1 grau ≈ 111 km
        dist_km = math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111

        # Se não estiverem conectados, penalizar
        if no2 not in self.adjacencia.get(no1, []):
            dist_km *= 10  # Penalidade pesada para rotas inválidas

        self.distancias_cache[key] = dist_km
        return dist_km

    def calcular_distancia_rota(self, rota: List[int]) -> float:
        """
        Calcula a distância total de uma rota
        """
        if len(rota) < 2:
            return 0.0

        distancia_total = 0.0
        for i in range(len(rota) - 1):
            dist = self.calcular_distancia(rota[i], rota[i + 1])
            if dist == float('inf'):
                return float('inf')  # Rota inválida
            distancia_total += dist

        # Voltar ao ponto inicial (rota circular)
        dist = self.calcular_distancia(rota[-1], rota[0])
        if dist == float('inf'):
            return float('inf')
        distancia_total += dist

        return distancia_total


    ### Estrutura do Algoritmo genético para implementação no TSP
    def criar_individuo(self, pontos: List[int]) -> List[int]:
        """
        Cria um indivíduo (rota) aleatório
        """
        individuo = pontos.copy()
        random.shuffle(individuo)
        return individuo

    def criar_populacao(self, pontos: List[int]) -> List[List[int]]:
        """
        Cria a população inicial
        """
        populacao = []

        # Indivíduo guloso (heurística do vizinho mais próximo)
        populacao.append(self._criar_rota_gulosa(pontos))

        # Restante aleatório
        for _ in range(self.populacao_tamanho - 1):
            populacao.append(self.criar_individuo(pontos))

        return populacao

    def _criar_rota_gulosa(self, pontos: List[int]) -> List[int]:
        """
        Cria uma rota usando a heurística do vizinho mais próximo
        """
        if not pontos:
            return []

        nao_visitados = set(pontos)
        rota = []

        # Começar com um ponto aleatório
        atual = random.choice(pontos)
        rota.append(atual)
        nao_visitados.remove(atual)

        while nao_visitados:
            # Encontrar o vizinho mais próximo
            proximo = min(nao_visitados,
                         key=lambda x: self.calcular_distancia(atual, x))
            rota.append(proximo)
            nao_visitados.remove(proximo)
            atual = proximo

        return rota

    def avaliar_populacao(self, populacao: List[List[int]]) -> List[Tuple[List[int], float]]:
        """
        Avalia toda a população
        """
        avaliados = []
        for individuo in populacao:
            distancia = self.calcular_distancia_rota(individuo)
            avaliados.append((individuo, distancia))

        # Ordenar por distância (melhor = menor)
        avaliados.sort(key=lambda x: x[1])
        return avaliados

    def selecao_torneio(self, populacao_avaliada: List[Tuple[List[int], float]],
                        tamanho_torneio: int = 3) -> List[int]:
        """
        Seleção por torneio
        """
        # Selecionar candidatos aleatórios
        candidatos = random.sample(populacao_avaliada, tamanho_torneio)

        # Retornar o melhor (menor distância)
        melhor = min(candidatos, key=lambda x: x[1])
        return melhor[0].copy()

    def cruzamento_ox(self, pai1: List[int], pai2: List[int]) -> Tuple[List[int], List[int]]:
        """
        Cruzamento Order Crossover (OX) - preserva a ordem relativa
        """
        if len(pai1) <= 2:
            return pai1.copy(), pai2.copy()

        tamanho = len(pai1)

        # Selecionar dois pontos de corte
        ponto1 = random.randint(0, tamanho - 2)
        ponto2 = random.randint(ponto1 + 1, tamanho - 1)

        # Inicializar filhos
        filho1 = [None] * tamanho
        filho2 = [None] * tamanho

        # Copiar segmento do pai1 para filho1 e do pai2 para filho2
        for i in range(ponto1, ponto2 + 1):
            filho1[i] = pai1[i]
            filho2[i] = pai2[i]

        # Preencher o resto com os genes do outro pai
        def preencher_filho(filho: List, pai: List, outro_pai: List, ponto1: int, ponto2: int):
            pos = (ponto2 + 1) % tamanho
            for gene in pai:
                if gene not in filho:
                    while filho[pos] is not None:
                        pos = (pos + 1) % tamanho
                    filho[pos] = gene

        preencher_filho(filho1, pai2, pai1, ponto1, ponto2)
        preencher_filho(filho2, pai1, pai2, ponto1, ponto2)

        return filho1, filho2

    def mutacao_troca(self, individuo: List[int]) -> List[int]:
        """
        Mutação por troca de dois genes
        """
        if len(individuo) <= 1:
            return individuo

        mutado = individuo.copy()

        # Selecionar duas posições aleatórias
        pos1 = random.randint(0, len(mutado) - 1)
        pos2 = random.randint(0, len(mutado) - 1)

        # Trocar
        mutado[pos1], mutado[pos2] = mutado[pos2], mutado[pos1]

        return mutado 
    
    def executar(self, pontos: List[int], verbose: bool = True) -> Dict:
        """
        Executa o algoritmo genético

        Args:
            pontos: Lista de pontos (nós) a serem visitados
            verbose: Se True, mostra progresso

        Returns:
            Dicionário com resultados
        """
        if len(pontos) < 2:
            return {
                'rota': pontos,
                'distancia': 0,
                'geracoes': 0,
                'historico_melhores': [],
                'historico_medias': []
            }

        print(f"\n{'='*60}")
        print("ALGORITMO GENÉTICO PARA TSP")
        print(f"{'='*60}")
        print(f"Pontos a visitar: {len(pontos)}")
        print(f"Tamanho da população: {self.populacao_tamanho}")
        print(f"Gerações: {self.geracoes}")
        print(f"Taxa de mutação: {self.taxa_mutacao}")
        print(f"Taxa de cruzamento: {self.taxa_cruzamento}")
        print(f"Elitismo: {self.elitismo}")
        print(f"{'='*60}\n")

        start_time = time.time()

        # Criar população inicial
        populacao = self.criar_populacao(pontos)

        # Avaliar população inicial
        populacao_avaliada = self.avaliar_populacao(populacao)

        # Melhor solução inicial
        self.melhor_rota, self.melhor_distancia = populacao_avaliada[0]

        # Histórico
        self.historico_melhores = [self.melhor_distancia]
        self.historico_medias = [sum(d for _, d in populacao_avaliada) / len(populacao_avaliada)]

        # Evolução
        for geracao in range(self.geracoes):
            nova_populacao = []

            # Elitismo - preservar os melhores
            for i in range(self.elitismo):
                nova_populacao.append(populacao_avaliada[i][0].copy())

            # Criar novos indivíduos
            while len(nova_populacao) < self.populacao_tamanho:
                # Seleção
                pai1 = self.selecao_torneio(populacao_avaliada)
                pai2 = self.selecao_torneio(populacao_avaliada)

                # Cruzamento
                if random.random() < self.taxa_cruzamento:
                    filho1, filho2 = self.cruzamento_ox(pai1, pai2)
                else:
                    filho1, filho2 = pai1.copy(), pai2.copy()

                # Mutação
                if random.random() < self.taxa_mutacao:
                    filho1 = self.mutacao_troca(filho1)
                if random.random() < self.taxa_mutacao:
                    filho2 = self.mutacao_troca(filho2)

                # Adicionar à nova população
                nova_populacao.append(filho1)
                if len(nova_populacao) < self.populacao_tamanho:
                    nova_populacao.append(filho2)

            # Avaliar nova população
            populacao_avaliada = self.avaliar_populacao(nova_populacao)

            # Atualizar melhor solução
            if populacao_avaliada[0][1] < self.melhor_distancia:
                self.melhor_rota = populacao_avaliada[0][0]
                self.melhor_distancia = populacao_avaliada[0][1]

            # Registrar histórico
            self.historico_melhores.append(self.melhor_distancia)
            media = sum(d for _, d in populacao_avaliada) / len(populacao_avaliada)
            self.historico_medias.append(media)

            # Progresso
            if verbose and (geracao + 1) % 10 == 0:
                print(f"Geração {geracao + 1:4d}/{self.geracoes} | "
                      f"Melhor: {self.melhor_distancia:.2f} km | "
                      f"Média: {media:.2f} km")

        elapsed_time = time.time() - start_time

        # Resultados finais
        print(f"\n{'='*60}")
        print("RESULTADOS FINAIS")
        print(f"{'='*60}")
        print(f"Melhor distância: {self.melhor_distancia:.2f} km")
        print(f"Tamanho da rota: {len(self.melhor_rota)} pontos")
        print(f"Tempo de execução: {elapsed_time:.2f} segundos")
        print(f"Redução: {((self.historico_melhores[0] - self.melhor_distancia) / self.historico_melhores[0] * 100):.1f}%")
        print(f"{'='*60}")

        return {
            'rota': self.melhor_rota,
            'distancia': self.melhor_distancia,
            'geracoes': self.geracoes,
            'tempo_execucao': elapsed_time,
            'historico_melhores': self.historico_melhores,
            'historico_medias': self.historico_medias,
            'melhor_inicial': self.historico_melhores[0],
            'melhor_final': self.melhor_distancia
        }

    def get_melhor_rota(self) -> Tuple[List[int], float]:
        """
        Retorna a melhor rota encontrada
        """
        return self.melhor_rota, self.melhor_distancia

    def get_historico(self) -> Dict:
        """
        Retorna o histórico de evolução
        """
        return {
            'melhores': self.historico_melhores,
            'medias': self.historico_medias
        }
def executar_tsp_com_pontos(
        pontos: List[int],
        adjacencia: Dict[int, List[int]],
        nos: Dict[int, Dict],
        populacao_tamanho: int = 100,
        geracoes: int = 100,
        taxa_mutacao: float = 0.1,
        taxa_cruzamento: float = 0.8,
        elitismo: int = 2,
        verbose: bool = True
    ) -> Dict:
        # Criar instância do algoritmo
        ag = AlgoritmoGeneticoTSP(
        adjacencia=adjacencia,
        nos=nos,
        populacao_tamanho=populacao_tamanho,
        geracoes=geracoes,
        taxa_mutacao=taxa_mutacao,
        taxa_cruzamento=taxa_cruzamento,
        elitismo=elitismo
    )

        # Executar
        resultado = ag.executar(pontos, verbose=verbose)

        return resultado

def otimizar_rota_com_pontos_selecionados(
        pontos: List[int],
        adjacencia: Dict[int, List[int]],
        nos: Dict[int, Dict],
        **kwargs
    ) -> Dict:
        return executar_tsp_com_pontos(pontos, adjacencia, nos, **kwargs)
        


            

    

    