"""
Analisador de Conexões de Aeroportos
Trabalho de Teoria de Grafos

"""

import json
import heapq
from collections import deque

ARQUIVO_DADOS = "aeroportos_dados.json"


# ---------------------------------------------------------
# 1. Carregar dados e montar o grafo (lista de adjacência)
# ---------------------------------------------------------

def carregar_dados(caminho=ARQUIVO_DADOS):
    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)

    aeroportos_info = {}
    for a in dados["aeroportos"]:
        aeroportos_info[a["codigo"]] = a

    # grafo[origem] = [ {destino, duracao_min, preco_reais, companhia}, ... ]
    grafo = {codigo: [] for codigo in aeroportos_info}

    for voo in dados["voos"]:
        origem = voo["origem"]
        grafo.setdefault(origem, []).append(voo)

    return grafo, aeroportos_info


# ---------------------------------------------------------
# 2. Regra de preço nas escalas
# ---------------------------------------------------------
# Ideia: passagens com conexão costumam sair mais em conta que a soma
# "crua" das passagens avulsas (tarifa combinada). Simulamos isso com
# um desconto percentual sobre o preço total, proporcional ao número
# de escalas, limitado a um teto.

def preco_com_desconto(preco_total, numero_escalas):
    desconto_por_escala = 0.05      # 5% de desconto por escala
    desconto_maximo = 0.15          # teto de 15%
    desconto = min(numero_escalas * desconto_por_escala, desconto_maximo)
    return preco_total * (1 - desconto), desconto


# ---------------------------------------------------------
# 3. Rota direta
# ---------------------------------------------------------

def existe_rota_direta(grafo, origem, destino):
    for voo in grafo.get(origem, []):
        if voo["destino"] == destino:
            return voo
    return None


# ---------------------------------------------------------
# 4. BFS - rota com menos escalas (não olha peso)
# ---------------------------------------------------------

def bfs_menos_escalas(grafo, origem, destino):
    if origem == destino:
        return [origem]

    visitado = {origem}
    fila = deque([origem])
    predecessor = {}

    while fila:
        atual = fila.popleft()

        for voo in grafo.get(atual, []):
            vizinho = voo["destino"]
            if vizinho not in visitado:
                visitado.add(vizinho)
                predecessor[vizinho] = atual

                if vizinho == destino:
                    return reconstruir_caminho(predecessor, origem, destino)

                fila.append(vizinho)

    return None  # não existe caminho (grafo desconexo)


def reconstruir_caminho(predecessor, origem, destino):
    caminho = [destino]
    atual = destino
    while atual != origem:
        atual = predecessor[atual]
        caminho.append(atual)
    caminho.reverse()
    return caminho


# ---------------------------------------------------------
# 5. Dijkstra - menor caminho por duração OU por preço
# ---------------------------------------------------------

def dijkstra(grafo, origem, destino, criterio="duracao_min"):
    """
    criterio: "duracao_min" (voo mais rápido) ou "preco_reais" (voo mais barato)
    """
    dist = {v: float("inf") for v in grafo}
    dist[origem] = 0
    predecessor = {}
    visitado = set()

    fila = [(0, origem)]  # (distancia, vertice)

    while fila:
        dist_atual, atual = heapq.heappop(fila)

        if atual in visitado:
            continue
        visitado.add(atual)

        if atual == destino:
            break

        for voo in grafo.get(atual, []):
            vizinho = voo["destino"]
            peso = voo[criterio]
            nova_dist = dist_atual + peso

            if nova_dist < dist[vizinho]:
                dist[vizinho] = nova_dist
                predecessor[vizinho] = atual
                heapq.heappush(fila, (nova_dist, vizinho))

    if dist[destino] == float("inf"):
        return None

    caminho = reconstruir_caminho(predecessor, origem, destino)
    return caminho


# ---------------------------------------------------------
# 6. Funções auxiliares de exibição
# ---------------------------------------------------------

def buscar_voo(grafo, origem, destino):
    """Pega os dados do voo direto entre dois vértices consecutivos do caminho."""
    for voo in grafo[origem]:
        if voo["destino"] == destino:
            return voo
    return None


def detalhar_caminho(grafo, caminho):
    """A partir de uma lista de aeroportos, soma duração e preço reais do trajeto."""
    duracao_total = 0
    preco_total = 0
    trechos = []

    for i in range(len(caminho) - 1):
        voo = buscar_voo(grafo, caminho[i], caminho[i + 1])
        trechos.append(voo)
        duracao_total += voo["duracao_min"]
        preco_total += voo["preco_reais"]

    escalas = len(caminho) - 2  # número de paradas intermediárias
    if escalas < 0:
        escalas = 0

    preco_final, desconto = preco_com_desconto(preco_total, escalas)

    return {
        "caminho": caminho,
        "trechos": trechos,
        "escalas": escalas,
        "duracao_total": duracao_total,
        "preco_bruto": preco_total,
        "preco_final": preco_final,
        "desconto_aplicado": desconto,
    }


def exibir_resultado(info, aeroportos_info):
    if info is None:
        print(">> Não existe rota disponível entre esses aeroportos.\n")
        return

    caminho = info["caminho"]
    nomes = " -> ".join(caminho)
    print(f"Rota: {nomes}")
    print(f"Número de escalas: {info['escalas']}")

    for voo in info["trechos"]:
        print(f"   {voo['origem']} -> {voo['destino']} | "
              f"{voo['duracao_min']} min | R$ {voo['preco_reais']:.2f} | {voo['companhia']}")

    h = info["duracao_total"] // 60
    m = info["duracao_total"] % 60
    print(f"Duração total: {info['duracao_total']} min ({h}h{m:02d})")

    if info["escalas"] > 0:
        print(f"Preço somado dos trechos: R$ {info['preco_bruto']:.2f}")
        print(f"Desconto por conexão ({info['desconto_aplicado']*100:.0f}%): "
              f"R$ {info['preco_final']:.2f}")
    else:
        print(f"Preço: R$ {info['preco_final']:.2f}")
    print()


# ---------------------------------------------------------
# 7. Menu principal
# ---------------------------------------------------------

def menu():
    grafo, aeroportos_info = carregar_dados()

    print("=" * 55)
    print(" ANALISADOR DE CONEXÕES DE AEROPORTOS - BRASIL")
    print("=" * 55)
    print(f"{len(aeroportos_info)} aeroportos carregados.\n")

    while True:
        print("1 - Verificar rota direta")
        print("2 - Rota com menos escalas (BFS)")
        print("3 - Rota mais rápida (Dijkstra por duração)")
        print("4 - Rota mais barata (Dijkstra por preço)")
        print("5 - Listar aeroportos disponíveis")
        print("0 - Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "0":
            print("Até mais!")
            break

        elif opcao == "5":
            for cod, info in sorted(aeroportos_info.items()):
                print(f"  {cod} - {info['cidade']}/{info['estado']}")
            print()
            continue

        origem = input("Aeroporto de origem (código, ex: GRU): ").strip().upper()
        destino = input("Aeroporto de destino (código, ex: REC): ").strip().upper()
        print()

        if origem not in aeroportos_info or destino not in aeroportos_info:
            print(">> Código de aeroporto inválido.\n")
            continue

        if opcao == "1":
            voo = existe_rota_direta(grafo, origem, destino)
            if voo:
                print(f"Existe voo direto {origem} -> {destino}")
                print(f"   {voo['duracao_min']} min | R$ {voo['preco_reais']:.2f} | {voo['companhia']}\n")
            else:
                print(f">> Não há voo direto entre {origem} e {destino}.\n")

        elif opcao == "2":
            caminho = bfs_menos_escalas(grafo, origem, destino)
            info = detalhar_caminho(grafo, caminho) if caminho else None
            exibir_resultado(info, aeroportos_info)

        elif opcao == "3":
            caminho = dijkstra(grafo, origem, destino, criterio="duracao_min")
            info = detalhar_caminho(grafo, caminho) if caminho else None
            exibir_resultado(info, aeroportos_info)

        elif opcao == "4":
            caminho = dijkstra(grafo, origem, destino, criterio="preco_reais")
            info = detalhar_caminho(grafo, caminho) if caminho else None
            exibir_resultado(info, aeroportos_info)

        else:
            print(">> Opção inválida.\n")


if __name__ == "__main__":
    menu()
