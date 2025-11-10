# Documentação do Projeto de Verificação de Grafos Bipartidos

## Contexto e objetivo
- **Propósito**: oferecer uma biblioteca Python para carregar grafos não direcionados, verificar bipartição via busca em largura (BFS) e expor os resultados por linha de comando ou visualizações interativas.
- **Domínio**: análise de relações entre dois grupos distintos (ex.: usuários e filmes, times e partidas, pessoas e tarefas), com ênfase em detectar conflitos que inviabilizam uma bipartição.
- **Fluxo principal**: um grafo é carregado a partir de arquivos texto, processado por `GrafoBipartido` e os resultados são exibidos como relatório textual, JSON ou animação.

## Estrutura do código
- `src/main.py`: CLI que aceita o caminho do arquivo, executa `GrafoBipartido.verificar_biparticao()` e oferece opções para JSON, visualização estática e animação (`--plot`, `--animar`, `--exportar-animacao`).
- `src/grafo/bipartido.py`: núcleo do domínio com as classes `GrafoBipartido`, `ResultadoBiparticao` e `PassoBiparticao`. Implementa BFS multi-componente, registra conflitos e expõe utilitários para consumir o resultado em outras camadas.
- `src/grafo/io.py`: rotinas de parsing para o formato textual, com suporte opcional à seção `[vertices]`, atributos extras e coordenadas explícitas.
- `src/grafo/visualizacao.py`: usa `networkx` e `matplotlib` para gerar visualizações, destacar partições, evidenciar conflitos e animar os passos capturados por `PassoBiparticao`.
- `scripts/gerar_midias.py`: facilita a geração de capturas estáticas e GIFs sem interface gráfica, reaproveitando o BFS interno para montar quadros intermediários.
- `exemplos/`: arquivos de entrada prontos (bipartido, não bipartido e cenários usuário–filme) úteis para validação manual e demonstração.

## Formato dos arquivos de entrada
Os grafos são descritos em arquivos `.txt` compatíveis com `carregar_de_arquivo`:

```text
[vertices]
<identificador> [pos=x,y | x=<float> y=<float>] [outros_atributos]
[arestas]
<identificador_origem> <identificador_destino>
```

- Comentários iniciados por `#` são ignorados.
- A seção `[vertices]` é opcional; quando omitida, o arquivo pode listar apenas as arestas.
- Coordenadas podem ser fornecidas com `pos=x,y` ou pares `x=…`/`y=…`; os valores são usados para fixar a posição de vértices nas visualizações.
- A seção `[arestas]` lista conexões não direcionadas; vértices ausentes nessa seção são inferidos a partir das arestas declaradas.

## Passo a passo do algoritmo
1. **Inicialização**: `GrafoBipartido._executar_bfs` cria dicionários vazios para cores e conflitos e, opcionalmente, uma lista de `PassoBiparticao` para animação.
2. **Processamento por componente**: para cada vértice ainda não colorido, o algoritmo inicia uma nova BFS, define a cor 0 e insere na fila (garantindo cobertura de componentes desconexos).
3. **Expansão BFS**: enquanto a fila não está vazia, remove o vértice atual, calcula a cor oposta e percorre todos os vizinhos.
4. **Coloração**: vizinhos não coloridos recebem a cor oposta e são adicionados à fila; um passo é registrado descrevendo a operação.
5. **Detecção de conflitos**: se um vizinho já colorido tem a mesma cor do vértice atual, a aresta é marcada como conflito e adicionada ao relatório.
6. **Resultado**: ao final da BFS de todas as componentes, o grafo é considerado bipartido caso a lista de conflitos esteja vazia. As partições são derivadas das cores atribuídas.
7. **Integração com visualização**: cada `PassoBiparticao` captura vértice ativo, fila, cores parciais e conflitos para que `animar_verificacao` atualize nós, arestas e painel textual quadro a quadro.

## Relação com a aplicação visual
- A CLI (`src/main.py`) delega a `visualizacao.exibir_grafo` para mostrar a coloração final com legendas de partições e conflitos, respeitando coordenadas fornecidas no arquivo.
- `visualizacao.animar_verificacao` transforma a sequência de `PassoBiparticao` em uma animação `matplotlib.FuncAnimation`, indicando vértice em processamento, fila e arestas conflitantes em tempo real.
- O script `scripts/gerar_midias.py` oferece comandos automatizados para produzir imagens e GIFs diretamente no diretório `docs/imagens/`, útil para apresentações e documentação.
- Arquivos de exemplo em `exemplos/` demonstram cenários bipartidos (`bipartido.txt`) e não bipartidos (`nao_bipartido.txt`), além de grafos usuário–filme prontos para visualização.

## Referências e links
- **Referência teórica**: Robert Sedgewick; Kevin Wayne. *Algorithms*, 4ª edição, Addison-Wesley, 2011. Capítulo 4 (Grafos) descreve a verificação de bipartição por BFS.
- **Datasets recomendados**: MovieLens (https://grouplens.org/datasets/movielens/) para grafos usuário–filme; bipartições acadêmicas disponíveis em https://snap.stanford.edu/data/.
- **Apresentação**: [Slides “Verificação de grafos bipartidos por BFS”](slides-biparticao.md).
- **Planilha**: [Planilha de acompanhamento de testes](https://docs.google.com/spreadsheets/d/1L5ExamplePlanilhaBipartido).
- **Vídeo**: [Demonstração da animação de coloração](https://youtu.be/ExampleVideoBipartido).
- **Documentação complementar**: teste de mesa detalhado (`teste-de-mesa.md`) e guia dos datasets usuário–filme (`usuario-filme-datasets.md`).
