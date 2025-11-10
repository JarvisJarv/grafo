---
title: Verificação de grafos bipartidos por BFS
subtitle: Algoritmo de coloração em dois conjuntos
---

# Motivação
- Grafos bipartidos modelam relacionamentos entre dois grupos distintos.
- A verificação de bipartição evita ciclos ímpares e garante coloração com duas cores.
- Útil em problemas de alocação, pareamento e redes sem conflitos.

---

# Objetivos da apresentação
1. Revisar conceitos fundamentais de bipartição.
2. Entender o funcionamento do algoritmo de coloração via busca em largura (BFS).
3. Observar a ferramenta visual em ação.
4. Explorar aplicações práticas em diferentes domínios.

---

# Conceitos-chave
- **Grafo não direcionado** \(G = (V, E)\).
- **Bipartição**: divisão de \(V\) em dois conjuntos \(V_0\) e \(V_1\) sem arestas internas.
- **Coloração binária**: atribuir cor 0 ou 1 a cada vértice respeitando as arestas.
- **Conflito**: aresta com vértices da mesma cor → indica ciclo ímpar.

---

# Estrutura do algoritmo
1. Percorre cada componente conectado do grafo.
2. Escolhe um vértice inicial e atribui a cor 0.
3. Executa BFS, alternando as cores dos vizinhos.
4. Registra conflitos (arestas com a mesma cor em ambos os extremos).
5. O grafo é bipartido se nenhum conflito for encontrado.

---

# Pseudocódigo simplificado
```
cores = {}
conflitos = []
para cada vértice não visitado:
    cores[v] = 0
    fila = [v]
    enquanto fila:
        atual = fila.pop(0)
        para cada vizinho de atual:
            se vizinho não colorido:
                cores[vizinho] = 1 - cores[atual]
                fila.append(vizinho)
            senão se cores[vizinho] == cores[atual]:
                conflitos.append((atual, vizinho))
```

---

# Complexidade e características
- **Tempo**: \(O(|V| + |E|)\) — cada vértice e aresta é visitado uma vez.
- **Espaço**: \(O(|V|)\) para armazenar cores e fila.
- Funciona em grafos desconectados (componentes independentes).
- Detecta automaticamente ciclos ímpares (conflitos).

---

# Visualização estática
> **Pré-requisito**: execute `python scripts/gerar_midias.py` para materializar as mídias em `docs/imagens/`.

![Visualização de um grafo bipartido colorido](imagens/visualizacao_bipartido.png)

Legenda automática destaca partições e conflitos (se existirem).

---

# Animação do processo de coloração
![Animação do BFS identificando conflito](imagens/animacao_coloracao.gif)

Cada quadro indica o vértice colorido ou conflito detectado durante a BFS.

---

# Aplicações
- Alocação estudante–projeto e emparelhamento em redes bipartidas.
- Modelagem de restrições de conflitos (ex.: agendamento de exames).
- Detecção de ciclos ímpares em grafos gerais.
- Base para algoritmos de pareamento máximo em grafos bipartidos.

---

# Recursos do projeto
- CLI: `python -m src.main exemplos/bipartido.txt --json`
- Visualização: `python -m src.main exemplos/nao_bipartido.txt --plot`
- Geração de mídias: `python scripts/gerar_midias.py`
- As imagens geradas ficam em `docs/imagens/` e são ignoradas pelo Git.
- Documentação complementar: consulte o teste de mesa em `docs/teste-de-mesa.md`.

