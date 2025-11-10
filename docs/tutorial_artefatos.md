# Guia completo dos artefatos do trabalho

Este tutorial organiza tudo o que já está pronto no repositório de acordo com os seis tópicos exigidos pela atividade. Para cada
artefato você verá:

- onde o código ou material está localizado;
- como executar ou visualizar o resultado;
- qual parte pode ser considerada "front-end" (visualização) e qual é somente lógica;
- como relacionar a entrega ao tema de recomendação de filmes e séries (pessoas × filmes).

> 💡 **Pré-requisito rápido:** instale as dependências antes de seguir os passos que usam Python.
> ```bash
> python -m venv .venv && source .venv/bin/activate
> pip install -r requirements.txt
> ```

## Visão geral (checklist rápido)

| Tópico da atividade | Artefatos principais | Como rodar ou acessar |
|---------------------|----------------------|------------------------|
| 1. Algoritmo | `src/grafo/bipartido.py`, testes em `tests/` | `pytest` ou `python -m src.main exemplos/arquivo.txt` |
| 2. Projeto com visualização ("front-end") | CLI em `src/main.py`, utilidades em `src/grafo/visualizacao.py`, script `scripts/gerar_midias.py` | `python -m src.main ... --plot/--animar` ou `python scripts/gerar_midias.py` |
| 3. Apresentação | `docs/apresentacao/slides-biparticao.md`, roteiro em `docs/apresentacao/README.md` | Renderize com Marp, Typora ou VS Code + Marp; use as mídias exportadas |
| 4. Arquivos `.txt` | Pasta `exemplos/` + guia `docs/trabalho/usuario-filme-datasets.md` | Abra/edite os `.txt`; valide com a CLI |
| 5. Teste de mesa (planilha) | `docs/trabalho/teste-de-mesa.md` + template de colunas | Importe a tabela para Excel/Planilhas Google |
| 6. Animação do algoritmo | CLI com `--animar`/`--exportar-animacao` ou `scripts/gerar_midias.py` | `python -m src.main ... --animar` / `python scripts/gerar_midias.py` |

---

## 1. Algoritmo sobre grafo bipartido (recomendação pessoa × filme)

**Onde está:** `src/grafo/bipartido.py` contém a classe `GrafoBipartido`, que executa a busca em largura (BFS) para colorir o grafo em duas partições.

**Como rodar sozinho (modo biblioteca):**
```bash
python - <<'PY'
from grafo.bipartido import GrafoBipartido

grafo = GrafoBipartido()
grafo.carregar_de_arquivo("exemplos/usuario_filme_equilibrado.txt")
resultado = grafo.verificar_biparticao()
print("É bipartido?", resultado.eh_bipartido)
print("Partições:", resultado.particoes)
print("Conflitos:", resultado.conflitos)
PY
```

**Como validar automaticamente:**
```bash
pytest
```
Os testes em `tests/` cobrem leitura dos arquivos, execução do algoritmo e geração de passos para animação.

**O que é front-end aqui?** Nenhum; é apenas a camada de lógica. O front-end aparece no tópico 2.

---

## 2. Projeto com visualização do grafo (front-end)

**Onde está:**
- `src/main.py` expõe uma interface de linha de comando (CLI) que carrega o `.txt`, executa o algoritmo e exibe resultados.
- `src/grafo/visualizacao.py` concentra o desenho estático e a animação (usando `matplotlib`/`networkx`).
- `scripts/gerar_midias.py` gera imagens e GIFs sem precisar abrir janelas.

**Rodando a CLI (visualização interativa):**
```bash
python -m src.main exemplos/usuario_filme_equilibrado.txt --plot
```
Adicione `--animar` para ver a execução passo a passo ou `--exportar-animacao docs/imagens/demo.gif` para salvar a animação. Consulte o [guia específico da CLI](tutorial_cli.md) para detalhes de cada opção.

**Gerando mídias automaticamente (útil para o front-end da apresentação):**
```bash
python scripts/gerar_midias.py
```
Isso cria `docs/imagens/visualizacao_bipartido.png` e `docs/imagens/animacao_coloracao.gif` a partir dos arquivos em `exemplos/`.

**O que mostrar como front-end:**
- A janela aberta pelo `--plot` evidencia as partições (usuários × filmes) com cores diferentes.
- A animação (`--animar` ou o GIF gerado) mostra a BFS pintando cada vértice, ideal para a aplicação prática exigida.

---

## 3. Apresentação de 20 minutos

**Onde está:**
- Slides em Markdown: `docs/apresentacao/slides-biparticao.md`.
- Resumo e referências: `docs/apresentacao/README.md`.

**Como utilizar:**
1. Abra os slides com uma ferramenta que renderize Markdown em formato de apresentação (ex.: [Marp](https://marp.app/), VS Code com extensão Marp, ou Typora).
2. Incorpore as imagens/animações geradas pelo tópico 2 (estão em `docs/imagens/`).
3. Siga a estrutura dos slides: conceitos → ideia geral → animação → teste de mesa → aplicações.

**Dicas:**
- Atualize os últimos slides com métricas ou observações do seu próprio experimento com pessoas × filmes.
- Utilize o roteiro do `README` dessa pasta para preparar a fala em 20 minutos.

---

## 4. Arquivos texto para gerar grafos

**Onde está:**
- Exemplos prontos: `exemplos/` (`bipartido.txt`, `nao_bipartido.txt`, `usuario_filme_equilibrado.txt`, `usuario_filme_tendencias.txt`, etc.).
- Documentação do formato: `docs/trabalho/usuario-filme-datasets.md`.

**Como criar e validar um novo arquivo:**
1. Copie um arquivo existente dentro de `exemplos/` e ajuste os pares `pessoa filme`.
2. Rode a CLI para checar se continua bipartido:
   ```bash
   python -m src.main exemplos/meu_arquivo.txt --json
   ```
3. Se houver conflitos (arestas unindo vértices do mesmo tipo), revise o `.txt` até o grafo ficar correto para a recomendação.

**Por que isso atende ao tópico:** você entrega pelo menos dois `.txt` distintos (um bipartido e outro com conflito) demonstrando cenários diferentes do algoritmo.

---

## 5. Teste de mesa (planilha estilo Excel)

**Onde está:** `docs/trabalho/teste-de-mesa.md` descreve passo a passo a execução do algoritmo em um grafo com ciclo ímpar.

**Como transformar em planilha:**
1. Abra o arquivo `.md` e copie a tabela principal (colunas: Passo, Operação, Vértice atual, etc.).
2. Cole em uma planilha do Excel ou Google Sheets. O Markdown já está alinhado em colunas.
3. Acrescente colunas extras, se quiser, para métricas personalizadas (por exemplo, "Partição Pessoas" e "Partição Filmes").
4. Exporte a planilha final (`.xlsx`) para anexar ao trabalho. Essa planilha faz referência direta ao algoritmo executado pela CLI.

**Dica:** mantenha um link ou captura da planilha em `docs/imagens/` para incorporar na apresentação.

---

## 6. Animação do algoritmo (vídeo)

**Opção 1 – direto pela CLI:**
```bash
python -m src.main exemplos/nao_bipartido.txt --animar --exportar-animacao docs/imagens/nao_bipartido.mp4 --fps 2
```
- `--animar`: mostra na tela (se estiver apresentando ao vivo).
- `--exportar-animacao`: salva o vídeo/GIF no caminho indicado para ser usado na apresentação.

**Opção 2 – uso do script automatizado:**
```bash
python scripts/gerar_midias.py
```
Esse comando produz automaticamente uma imagem e um GIF padronizados. Ideal quando você quiser regenerar os arquivos antes de apresentar.

**Como usar no trabalho:** inclua o GIF ou MP4 na apresentação (tópico 3) e mostre que a animação reflete exatamente as etapas documentadas no teste de mesa (tópico 5).

---

## Próximos passos sugeridos
- Adapte os exemplos de `exemplos/` para representar usuários reais e categorias de filmes/series que você deseja recomendar.
- Atualize os slides e a planilha com insights obtidos ao rodar o algoritmo nos seus próprios dados.
- Utilize o script de mídias antes da apresentação para garantir que todo o material visual esteja sincronizado com a versão mais recente do código.

Com este guia você consegue navegar rapidamente entre código, visualização, documentação e materiais de apresentação, cobrindo todos os tópicos da atividade.
