# # otimizador_rotas.py
"""
Módulo para otimização de rotas TSP - Eliminação de Cruzamentos
"""

from typing import List, Dict, Tuple, Optional
import math

class OtimizadorRotas:
    """
    Classe para otimizar rotas TSP eliminando cruzamentos
    """

    def __init__(self, nos: Dict[int, Dict]):
        """
        Inicializa o otimizador

        Args:
            nos: Dicionário com informações dos nós
        """
        self.nos = nos
        self.cache_distancias = {}

    def calcular_distancia(self, no1: int, no2: int) -> float:
        """
        Calcula a distância entre dois nós
        """
        key = tuple(sorted([no1, no2]))
        if key in self.cache_distancias:
            return self.cache_distancias[key]

        info1 = self.nos.get(no1, {})
        info2 = self.nos.get(no2, {})

        lat1 = info1.get('latitude')
        lon1 = info1.get('longitude')
        lat2 = info2.get('latitude')
        lon2 = info2.get('longitude')

        if lat1 is None or lat2 is None:
            dist = 1000000.0  # Penalidade alta
            self.cache_distancias[key] = dist
            return dist

        # Distância euclidiana (em km)
        dist = math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111
        self.cache_distancias[key] = dist
        return dist

    def calcular_distancia_rota(self, rota: List[int]) -> float:
        """
        Calcula a distância total de uma rota
        """
        if len(rota) < 2:
            return 0.0

        distancia_total = 0.0
        for i in range(len(rota) - 1):
            distancia_total += self.calcular_distancia(rota[i], rota[i + 1])

        # Voltar ao início
        distancia_total += self.calcular_distancia(rota[-1], rota[0])

        return distancia_total

    def _orientacao(self, p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> int:
        """
        Calcula a orientação de três pontos
        Retorna: 0 = colinear, 1 = horário, 2 = anti-horário
        """
        val = (p2[1] - p1[1]) * (p3[0] - p2[0]) - (p2[0] - p1[0]) * (p3[1] - p2[1])
        if abs(val) < 1e-10:
            return 0
        return 1 if val > 0 else 2

    def _segmentos_se_cruzam(self, a1: Tuple[float, float], a2: Tuple[float, float],
                             b1: Tuple[float, float], b2: Tuple[float, float]) -> bool:
        """
        Verifica se dois segmentos se cruzam
        """
        o1 = self._orientacao(a1, a2, b1)
        o2 = self._orientacao(a1, a2, b2)
        o3 = self._orientacao(b1, b2, a1)
        o4 = self._orientacao(b1, b2, a2)

        # Caso geral
        if o1 != o2 and o3 != o4:
            return True

        # Casos especiais (colineares)
        if o1 == 0 and self._no_segmento(a1, a2, b1):
            return True
        if o2 == 0 and self._no_segmento(a1, a2, b2):
            return True
        if o3 == 0 and self._no_segmento(b1, b2, a1):
            return True
        if o4 == 0 and self._no_segmento(b1, b2, a2):
            return True

        return False

    def _no_segmento(self, p: Tuple[float, float], q: Tuple[float, float],
                     r: Tuple[float, float]) -> bool:
        """
        Verifica se o ponto r está no segmento pq
        """
        return (min(p[0], q[0]) <= r[0] <= max(p[0], q[0]) and
                min(p[1], q[1]) <= r[1] <= max(p[1], q[1]))

    def _ha_cruzamento(self, rota: List[int], i: int, j: int) -> bool:
        """
        Verifica se há cruzamento entre as arestas (i, i+1) e (j, j+1)
        """
        if len(rota) < 4:
            return False

        # Pega as coordenadas dos 4 pontos
        def get_coords(no_id):
            info = self.nos.get(no_id, {})
            return (info.get('longitude', 0), info.get('latitude', 0))

        a1 = get_coords(rota[i])
        a2 = get_coords(rota[(i + 1) % len(rota)])
        b1 = get_coords(rota[j])
        b2 = get_coords(rota[(j + 1) % len(rota)])

        return self._segmentos_se_cruzam(a1, a2, b1, b2)

    def contar_cruzamentos(self, rota: List[int]) -> int:
        """
        Conta o número de cruzamentos em uma rota
        """
        if len(rota) < 4:
            return 0

        cruzamentos = 0
        for i in range(len(rota)):
            for j in range(i + 2, len(rota)):
                if self._ha_cruzamento(rota, i, j):
                    cruzamentos += 1

        return cruzamentos

    def aplicar_2opt(self, rota: List[int], max_iteracoes: int = 1000) -> Tuple[List[int], float, int]:
        """
        Aplica o algoritmo 2-opt para eliminar cruzamentos

        Args:
            rota: Lista de IDs dos nós na rota
            max_iteracoes: Número máximo de iterações

        Returns:
            Tupla (rota_melhorada, distancia, cruzamentos_eliminados)
        """
        if len(rota) <= 3:
            return rota, self.calcular_distancia_rota(rota), 0

        melhor = rota.copy()
        distancia_atual = self.calcular_distancia_rota(melhor)
        cruzamentos_iniciais = self.contar_cruzamentos(melhor)

        melhorou = True
        iteracoes = 0

        while melhorou and iteracoes < max_iteracoes:
            melhorou = False
            iteracoes += 1

            for i in range(len(melhor) - 2):
                for j in range(i + 2, len(melhor)):
                    # Verifica se há cruzamento
                    if self._ha_cruzamento(melhor, i, j):
                        # Inverte o segmento para eliminar o cruzamento
                        nova = melhor.copy()
                        nova[i+1:j+1] = reversed(nova[i+1:j+1])

                        # Verifica se melhorou
                        nova_dist = self.calcular_distancia_rota(nova)

                        if nova_dist < distancia_atual:
                            melhor = nova
                            distancia_atual = nova_dist
                            melhorou = True
                            break
                if melhorou:
                    break

        cruzamentos_finais = self.contar_cruzamentos(melhor)

        return melhor, distancia_atual, cruzamentos_iniciais - cruzamentos_finais

    def otimizar_rota_completa(self, rota: List[int]) -> Dict:
        """
        Otimiza a rota completa e retorna estatísticas

        Args:
            rota: Lista de IDs dos nós na rota

        Returns:
            Dicionário com resultados
        """
        print("\n" + "="*60)
        print("OTIMIZAÇÃO 2-OPT - ELIMINANDO CRUZAMENTOS")
        print("="*60)

        # Estatísticas iniciais
        dist_inicial = self.calcular_distancia_rota(rota)
        cruz_inicial = self.contar_cruzamentos(rota)

        print(f"\n📊 ANTES DA OTIMIZAÇÃO:")
        print(f"   Distância: {dist_inicial:.2f} km")
        print(f"   Cruzamentos: {cruz_inicial}")

        # Aplicar 2-opt
        rota_otimizada, dist_final, cruz_eliminados = self.aplicar_2opt(rota)
        cruz_final = self.contar_cruzamentos(rota_otimizada)

        print(f"\n📊 DEPOIS DA OTIMIZAÇÃO:")
        print(f"   Distância: {dist_final:.2f} km")
        print(f"   Cruzamentos: {cruz_final}")
        print(f"   Cruzamentos eliminados: {cruz_eliminados}")

        melhoria = ((dist_inicial - dist_final) / dist_inicial) * 100 if dist_inicial > 0 else 0
        print(f"   Melhoria: {melhoria:.2f}%")

        return {
            'rota_original': rota,
            'rota_otimizada': rota_otimizada,
            'distancia_original': dist_inicial,
            'distancia_otimizada': dist_final,
            'cruzamentos_original': cruz_inicial,
            'cruzamentos_otimizada': cruz_final,
            'cruzamentos_eliminados': cruz_eliminados,
            'melhoria_percentual': melhoria
        }


# ================================================================
# FUNÇÃO DE CONVENIÊNCIA
# ================================================================

def otimizar_rota_2opt(
    rota: List[int],
    nos: Dict[int, Dict],
    verbose: bool = True
) -> Dict:
    """
    Função de conveniência para otimizar uma rota com 2-opt

    Args:
        rota: Lista de IDs dos nós na rota
        nos: Dicionário com informações dos nós
        verbose: Se True, mostra progresso

    Returns:
        Dicionário com resultados
    """
    otimizador = OtimizadorRotas(nos)
    return otimizador.otimizar_rota_completa(rota)