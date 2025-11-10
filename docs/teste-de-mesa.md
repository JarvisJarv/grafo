# Teste de mesa: coloração BFS em grafo com ciclo ímpar

O exemplo utiliza o grafo do arquivo `exemplos/nao_bipartido.txt`, composto pelas arestas:
\(1-2\), \(2-3\) e \(3-1\). Trata-se de um triângulo e, portanto, não é bipartido.

## Estado inicial
- **Cores**: `{}` (nenhum vértice colorido).
- **Fila**: `[]`.
- **Conflitos**: `[]`.

O algoritmo percorre os vértices em ordem crescente.

## Passos detalhados

| Passo | Ação | Fila após a ação | Cores registradas | Conflitos |
|-------|------|------------------|-------------------|-----------|
| 1 | Escolhe vértice inicial **1**, define cor 0 e o coloca na fila | `[1]` | `1→0` | `—` |
| 2 | Remove **1** da fila. Vizinho **2** sem cor → atribui cor 1 e enfileira | `[2]` | `1→0, 2→1` | `—` |
| 3 | Ainda processando vizinhos de **1**: vizinho **3** sem cor → atribui cor 1 e enfileira | `[2, 3]` | `1→0, 2→1, 3→1` | `—` |
| 4 | Remove **2** da fila. Vizinho **1** já colorido com cor diferente → nada muda | `[3]` | `1→0, 2→1, 3→1` | `—` |
| 5 | Vizinho **3** de **2** já colorido com **1** → detecta conflito (mesma cor) | `[3]` | `1→0, 2→1, 3→1` | `(2, 3)` |
| 6 | Remove **3** da fila. Vizinho **1** já colorido com cor diferente → nada muda | `[]` | `1→0, 2→1, 3→1` | `(2, 3)` |
| 7 | Vizinho **2** de **3** também cor 1 → registra conflito já conhecido | `[]` | `1→0, 2→1, 3→1` | `(2, 3)` |

## Resultado final
- **Cores**: vértice 1 → cor 0; vértices 2 e 3 → cor 1.
- **Conflitos**: aresta \((2, 3)\) mantém a mesma cor em ambos os extremos.
- **Conclusão**: o grafo NÃO é bipartido, pois contém um ciclo ímpar.

> Dica: execute `python -m src.main exemplos/nao_bipartido.txt --json` para obter o mesmo resultado pela CLI. As mídias podem ser (re)geradas com `python scripts/gerar_midias.py` e ficam disponíveis em `docs/imagens/`.

