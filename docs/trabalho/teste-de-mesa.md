# Teste de mesa: coloração BFS em grafo com ciclo ímpar

O exemplo utiliza o grafo do arquivo `exemplos/nao_bipartido.txt`, composto pelas arestas:
\(1-2\), \(2-3\) e \(3-1\). Trata-se de um triângulo e, portanto, não é bipartido.

## Estado inicial
- **Cores**: `{}` (nenhum vértice colorido).
- **Fila**: `[]`.
- **Conflitos**: `[]`.

O algoritmo percorre os vértices em ordem crescente.

## Passos detalhados

| Passo | Operação | Vértice atual | Fila | Processados | Cores | Conflitos |
|-------|----------|---------------|------|-------------|-------|-----------|
| 1 | Escolhe vértice inicial **1**, define cor 0 e o coloca na fila | `—` | `[1]` | `[]` | `1→0` | `—` |
| 2 | Remove **1** da fila, visita vizinhos **2** e **3** (ambos recebem cor 1 e entram na fila) | `1` | `[2, 3]` | `[1]` | `1→0, 2→1, 3→1` | `—` |
| 3 | Remove **2** da fila, verifica vizinhos (conflito detectado entre **2** e **3** com mesma cor) | `2` | `[3]` | `[1, 2]` | `1→0, 2→1, 3→1` | `(2, 3)` |
| 4 | Remove **3** da fila, revisita vizinhos já processados e confirma conflito existente | `3` | `[]` | `[1, 2, 3]` | `1→0, 2→1, 3→1` | `(2, 3)` |

## Resultado final
- **Cores**: vértice 1 → cor 0; vértices 2 e 3 → cor 1.
- **Conflitos**: aresta \((2, 3)\) mantém a mesma cor em ambos os extremos.
- **Conclusão**: o grafo NÃO é bipartido, pois contém um ciclo ímpar.

> Dica: execute `python -m src.main exemplos/nao_bipartido.txt --json` para obter o mesmo resultado pela CLI. As mídias podem ser (re)geradas com `python scripts/gerar_midias.py` e ficam disponíveis em `docs/imagens/`.
