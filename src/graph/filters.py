ESTADOS = {"PR", "SC", "RS", "SP"}


def filtrar_nos(nos):
    """
    Mantém apenas os nós dos estados desejados.
    """

    nos_filtrados = {}

    for id_no, info in nos.items():

        if info["uf_principal"] in ESTADOS:
            nos_filtrados[id_no] = info

    return nos_filtrados

def filtrar_adjacencia(adjacencia, nos_filtrados):
    """
    Mantém apenas as conexões entre nós filtrados.
    """

    ids_validos = set(nos_filtrados.keys())

    nova_adjacencia = {}

    for origem, vizinhos in adjacencia.items():

        if origem not in ids_validos:
            continue

        nova_adjacencia[origem] = []

        for aresta in vizinhos:

            destino = str(aresta["destino"])

            if destino in ids_validos:
                nova_adjacencia[origem].append(aresta)

    print("\n");

    ESTADOS_SUL = {"PR", "SC", "RS"}

    for id_no, info in nos_filtrados.items():

        if info["uf_principal"] == "SP":

            for aresta in nova_adjacencia.get(id_no, []):

                destino = str(aresta["destino"])

                if destino in nos_filtrados:

                    estado_destino = nos_filtrados[destino]["uf_principal"]

                    if estado_destino in ESTADOS_SUL:
                        print(
                            f"SP conectado diretamente a "
                            f"{estado_destino}: "
                            f"{id_no} -> {destino}"
                    )
    print("\n");
    return nova_adjacencia


