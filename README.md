# Analisador de Conexões de Aeroportos

Trabalho de **Teoria de Grafos** — sistema que modela a malha aérea do Brasil
como um grafo dirigido e identifica rotas diretas, rotas com escalas e o
menor caminho entre dois aeroportos.

## Arquivos

| Arquivo | Descrição |
|---|---|
| `analisador_aeroportos.py` | Código principal (menu interativo) |
| `aeroportos_dados.json` | Dataset: 30 aeroportos + 132 voos diretos |
| `grafo_aeroportos.png` | Diagrama da malha aérea (para a apresentação) |

## Modelagem do grafo

- **Vértices**: aeroportos (código IATA)
- **Arestas**: voos diretos — **grafo dirigido**, pois um voo A→B não implica
  necessariamente B→A com o mesmo preço/duração
- **Peso da aresta**: cada voo tem dois pesos possíveis — `duracao_min` e
  `preco_reais` — permitindo rodar o mesmo algoritmo (Dijkstra) com
  critérios diferentes
- **Representação**: lista de adjacência (`dict` de listas em Python), mais
  eficiente que matriz de adjacência para um grafo esparso como esse

## Algoritmos e complexidade

| Funcionalidade | Algoritmo | Complexidade | O que otimiza |
|---|---|---|---|
| Rota direta | Busca na lista de adjacência | O(grau do vértice) | Existência de aresta |
| Rota com menos escalas | **BFS** | O(V + E) | Número de arestas (ignora peso) |
| Rota mais rápida | **Dijkstra** (peso = duração) | O((V + E) log V) | Soma de tempo de voo |
| Rota mais barata | **Dijkstra** (peso = preço) | O((V + E) log V) | Soma de preço |

Onde V = número de aeroportos (vértices) e E = número de voos (arestas).

A complexidade O((V + E) log V) do Dijkstra vem do uso de uma **fila de
prioridade** (`heapq` em Python) — sem ela, a versão ingênua seria O(V²).

### Por que BFS não serve para caminho mais barato/rápido?

BFS trata todas as arestas como se tivessem peso 1 — ele encontra o caminho
com **menor número de arestas** (menos escalas), não o de menor custo
acumulado. Por isso o projeto usa dois algoritmos diferentes: BFS para
"menos escalas" e Dijkstra para "menor custo" (tempo ou preço).

### Regra de preço nas escalas

O dataset já foi montado para que, em alguns trajetos longos, o **voo direto
seja mais caro** do que a soma de dois trechos com conexão (ex: `GRU → BEL`
direto custa R$ 890, mas `GRU → BSB → BEL` custa R$ 730 somado). Além disso,
o código aplica um **desconto de tarifa combinada**: 5% por escala, até um
teto de 15%, simulando o comportamento real de passagens com conexão.

```python
def preco_com_desconto(preco_total, numero_escalas):
    desconto = min(numero_escalas * 0.05, 0.15)
    return preco_total * (1 - desconto), desconto
```

Isso gera um ponto de discussão interessante no relatório: **menos escalas
não significa necessariamente mais barato** — BFS e Dijkstra-por-preço podem
devolver caminhos diferentes para o mesmo par origem-destino.

## Como testar no VS Code

1. **Pré-requisito**: ter Python 3 instalado (verifique com `python3 --version`
   ou `python --version` no terminal). Se não tiver, baixe em python.org.

2. **Extensão recomendada**: instale a extensão oficial **Python** (da
   Microsoft) no VS Code, pela aba de Extensões (ícone de quadrados na
   barra lateral, ou `Ctrl+Shift+X`).

3. **Organize os arquivos**: coloque `analisador_aeroportos.py` e
   `aeroportos_dados.json` **na mesma pasta**. O código lê o JSON pelo
   caminho relativo, então o VS Code precisa estar com essa pasta aberta
   (`Arquivo → Abrir Pasta...`).

4. **Rodar o programa**:
   - Abra `analisador_aeroportos.py`
   - Clique no botão ▶ (Run Python File) no canto superior direito, **ou**
   - Abra o terminal integrado (`` Ctrl+` ``) e rode:
     ```bash
     python3 analisador_aeroportos.py
     ```
     (no Windows, geralmente é só `python analisador_aeroportos.py`)

5. **Usar o menu**: o programa pede um número de opção e depois os códigos
   de origem/destino (ex: `GRU`, `BSB`, `REC`...). Use a opção **5** para
   listar todos os códigos disponíveis.

6. **Erro comum**: se aparecer
   `FileNotFoundError: [Errno 2] No such file or directory: 'aeroportos_dados.json'`,
   é porque o terminal não está na pasta certa. Rode `cd caminho/da/pasta`
   antes, ou confira se abriu a pasta correta no VS Code (não só o arquivo
   solto).

Não é necessário instalar nenhuma biblioteca externa — o projeto usa apenas
`json`, `heapq` e `collections`, que já vêm no Python padrão.

## Possíveis extensões (para nota extra)

- Detectar aeroportos sem conexão (componentes desconexos do grafo)
- Filtrar rotas por companhia aérea (evita troca de bagagem na conexão)
- Validar tempo mínimo de conexão entre voos
- Limitar o número máximo de escalas na busca
