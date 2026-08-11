# Projeto Logística Sul-SP

Projeto de busca de caminhos na malha rodoviária federal dos estados SP, PR, SC e RS, utilizando o algoritmo de Busca de Custo Uniforme (UCS).

---

## Estrutura do projeto

```
src/
├── main.py                  # Pipeline principal
├── algorithms/
│   ├── ucs.py               # Busca de Custo Uniforme
│   └── tsp.py               # (futuro) Problema do Caixeiro Viajante
├── graph/
│   ├── loader.py            # Carregamento do grafo (JSON)
│   ├── filters.py           # Filtro por estado (PR/SC/RS/SP)
│   ├── components.py        # Encontrar componentes conexos (DFS)
│   └── random_nodes.py      # Seleção aleatória de dois nós
└── visualization/
    └── plot_graph.py        # Visualização com NetworkX/Matplotlib
```

---

## Pipeline de execução (`main.py`)

1. **Carregar** o grafo do arquivo `data/grafo_adjacencia_enriquecido.json`
2. **Filtrar** apenas os nós dos estados SP, PR, SC, RS e as arestas entre eles
3. **Encontrar** os componentes conexos via DFS iterativo (`graph/components.py`)
4. **Executar UCS** em todos os componentes com 2 ou mais nós:
   - Seleciona dois nós aleatórios (`selecionar_dois_nos`)
   - Calcula o caminho de menor custo entre eles
   - Exibe caminho, rodovias, distância total e nós explorados
5. **Visualizar** o maior componente com origem/destino destacados

---

## Algoritmo: Busca de Custo Uniforme (UCS)

### Visão geral

A Busca de Custo Uniforme (Uniform Cost Search) é uma variação do algoritmo de Dijkstra adaptada para busca em grafos. Diferentemente do BFS (que expande pelo número de arestas), o UCS expande os nós em ordem crescente de custo acumulado desde a origem, garantindo que o primeiro caminho encontrado até o destino seja o de **menor custo total**.

O algoritmo é implementado em `src/algorithms/ucs.py`.

### Estruturas de dados

| Estrutura | Tipo | Propósito |
|---|---|---|
| `heap` | `list` gerenciada por `heapq` | Fila de prioridade (min-heap) com tuplas `(custo, nó, caminho_ids, rodovias)` |
| `visitados` | `dict` (`{nó: menor_custo}`) | Armazena o menor custo conhecido para alcançar cada nó; usado para poda |
| `explorados` | `int` | Contador de nós expandidos (iterações do loop principal) |

### Funcionamento passo a passo

**1. Inicialização**

```python
heap = [(0.0, origem, [origem], [None])]
visitados = {}
explorados = 0
```

- A heap começa com a origem, custo zero e o caminho contendo apenas o nó inicial.
- O primeiro elemento da lista `rodovias` é `None` (a origem não foi alcançada por rodovia alguma).

**2. Loop principal**

```python
while heap:
    custo, atual, caminho_ids, rodovias = heapq.heappop(heap)
    explorados += 1
```

- Remove da heap o nó com **menor custo acumulado** (propriedade do min-heap).
- Incrementa o contador de nós explorados.

**3. Condição de parada (goal test)**

```python
if atual == destino:
    return caminho_ids, rodovias, custo, explorados
```

- O teste de objetivo é feito **ao remover** da heap (não ao inserir), garantindo que o caminho retornado seja o de menor custo — um caminho mais barato poderia ainda estar na fila se o teste fosse feito na inserção.

**4. Poda por custo (controle de visitados)**

```python
if atual in visitados and visitados[atual] <= custo:
    continue

visitados[atual] = custo
```

- Se o nó já foi visitado com custo **menor ou igual**, descarta esta expansão (poda).
- Caso contrário, registra o novo custo mínimo no dicionário `visitados`.
- Isso é idêntico ao relaxamento do Dijkstra: um nó pode ser reinserido na heap múltiplas vezes com custos decrescentes, mas só a primeira expansão com custo mínimo é processada.

**5. Expansão de vizinhos**

```python
for aresta in adjacencia[atual]:
    vizinho = str(aresta["destino"])
    peso = aresta["distancia_km"]
    novo_custo = custo + peso

    if vizinho not in visitados or novo_custo < visitados[vizinho]:
        heapq.heappush(
            heap,
            (novo_custo, vizinho,
             caminho_ids + [vizinho],
             rodovias + [aresta["rodovia"]])
        )
```

- Para cada aresta saindo do nó atual:
  - Converte `aresta["destino"]` (int) para `str` — as chaves da adjacência são strings.
  - Obtém o peso da aresta: `aresta["distancia_km"]` (quilômetros).
  - Calcula o novo custo acumulado.
  - Se o vizinho nunca foi visitado **ou** o novo custo é menor que o registrado, insere na heap com o caminho e as rodovias atualizados.
- A rodovia usada (`aresta["rodovia"]`, ex: `"BR-050"`) é anexada à lista de rodovias para compor o trajeto completo.

**6. Sem caminho**

```python
return None
```

Se a heap esvaziar sem que o destino seja alcançado, não há caminho (componente desconexo ou erro).

### Por que usar heap de prioridade?

A heap garante que o nó com menor custo acumulado seja sempre processado primeiro. Sem ela, seria necessário percorrer toda a fronteira a cada iteração para encontrar o mínimo (custo `O(n)` por iteração). Com `heapq`, tanto a inserção quanto a remoção do mínimo são `O(log n)`.

### Complexidade

- **Tempo**: `O((V + E) log V)` — cada aresta pode gerar uma inserção na heap, e cada operação de heap custa `O(log V)`.
- **Espaço**: `O(V)` — a heap e o dicionário de visitados armazenam no máximo `V` entradas.

### Corretude

O UCS é correto (encontra o caminho de menor custo) para grafos com pesos **não-negativos** — condição satisfeita, pois `distancia_km > 0` para todas as arestas.

### Exemplo de saída

```
=== Componente 0 (1287 nós) ===
Origem: 336 | Destino: 338
Caminho: 336 -> 337 -> 338
Rodovias: (origem) -> BR-050 -> BR-050
Distância total: 45.67 km
Nós explorados pelo UCS: 12
```

---

## Formato dos dados

O grafo é carregado de `data/grafo_adjacencia_enriquecido.json` com a seguinte estrutura:

```json
{
  "metadados": { ... },
  "nos": {
    "336": {
      "id": 336,
      "latitude": -20.0446368,
      "longitude": -47.7808969,
      "uf_principal": "SP",
      "locais_associados": ["ACESSO OESTE IGARAPAVA"],
      ...
    }
  },
  "adjacencia": {
    "336": [
      {
        "destino": 337,
        "distancia_km": 23.45,
        "rodovia": "BR-050",
        ...
      }
    ]
  }
}
```

O custo utilizado pelo UCS é o campo `distancia_km` de cada aresta.

---

## Dependências

- `networkx` — construção e renderização do grafo
- `matplotlib` — salvamento da imagem PNG

Instalar com:

```bash
pip install -r requirements.txt
```

---

## Execução

```bash
cd src
python main.py
```
