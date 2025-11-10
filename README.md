# Projeto de Verificação de Grafo Bipartido

Este repositório reúne os artefatos desenvolvidos para o estudo de grafos bipartidos usando a relação Usuários × Filmes como cenário principal. Todo o material está organizado para que qualquer pessoa possa reproduzir o algoritmo, visualizar sua execução e estudar os resultados.

## Estrutura geral
- `src/`: código-fonte do verificador, leitor de arquivos texto e utilidades de visualização.
- `exemplos/`: coleções de arquivos `.txt` que definem os grafos utilizados nos testes e demonstrações.
- `docs/`: documentação técnica do trabalho, materiais de apresentação e guia de estudos.
- `scripts/`: automações para gerar animações, capturas e demais mídias de apoio.

## Entregáveis técnicos
- Implementação em Python do verificador de bipartição baseada em BFS (`src/grafo/bipartido.py`).
- Entrada de dados flexível via arquivos texto (`src/grafo/io.py`).
- Interface de linha de comando em `src/main.py` para executar o algoritmo, exportar JSON e acionar visualizações.
- Documentação de referência, teste de mesa e guia de datasets em `docs/trabalho/`.
- Exemplos variados dentro do diretório `exemplos/`, incluindo cenários bipartidos e não bipartidos baseados em Usuários × Filmes.

## Materiais de apresentação
- Slides com conceitos, teoria e demonstração em `docs/apresentacao/slides-biparticao.md`.
- Instruções para gerar animações, capturas e roteiro de apresentação em `docs/apresentacao/`.
- Planilha de acompanhamento descrita em `docs/trabalho/teste-de-mesa.md` e materiais de apoio citados no relatório.
- Guia integrando todos os entregáveis e explicando como rodar cada parte do projeto em [`docs/tutorial_artefatos.md`](docs/tutorial_artefatos.md).

## Como executar
Um passo a passo mais detalhado, com exemplos de combinações de opções da CLI, está em [`docs/tutorial_cli.md`](docs/tutorial_cli.md).

1. Instale as dependências: `pip install -r requirements.txt`.
2. Escolha um arquivo de entrada em `exemplos/`. Além dos clássicos `usuario_filme_equilibrado.txt` e `usuario_filme_tendencias.txt`, agora há pares pensados para a apresentação: `usuarios_filmes_recomendacao.txt` (bipartido, com Gabriel × Filmes) e `usuarios_filmes_conflito.txt` (contém um erro proposital entre Marcelo e Gabriel).
3. Rode o verificador com um arquivo de exemplo:
   - usando o módulo: `python -m src.main "exemplos/usuarios_filmes_recomendacao.txt" --plot`
   - executando diretamente: `python src/main.py exemplos/bipartido.txt --plot`
   - comando legado (caso esteja usando o arquivo antigo): `python -m src.main exemplos/usuario_filme_bipartido.txt --plot`
4. Para exportar uma animação: `python -m src.main exemplos/nao_bipartido.txt --animar --exportar-animacao docs/imagens/biparticao.gif`.

### Opções da CLI
- `--json`: imprime o resultado completo (partições, conflitos e posições) em formato JSON.
- `--plot`: abre uma visualização estática destacando as partições e conflitos.
- `--animar`: executa a animação dos passos do algoritmo.
- `--exportar-animacao CAMINHO`: salva a animação em GIF ou MP4 para o caminho informado.
- `--layout {spring,circular,kamada_kawai,bipartido}`: escolhe o algoritmo de posicionamento dos vértices.
- `--fps N`: define a taxa de quadros da animação ou exportação (valor mínimo 1).

## Interface gráfica moderna

Para quem prefere uma experiência visual completa, o projeto inclui uma aplicação
PySide6 que combina o verificador com um painel de visualização interativo.

1. Instale as dependências com suporte a Qt (`pip install -r requirements.txt`).
2. Execute `python -m grafo.interface` (o carregador automático garante que o
   módulo seja encontrado mesmo rodando direto do diretório raiz).
3. Escolha um arquivo `.txt` existente ou escreva um novo arquivo na aba "Criar
   arquivo .txt". A aplicação traz exemplos prontos (como Gabriel × Filmes) e um
   guia de formatação embutido.

Recursos disponíveis na interface:

- Diagrama com layout moderno e legendas coloridas para as partições.
- Destaque automático das arestas conflitantes em vermelho.
- Painel com o resumo do algoritmo (partições, quantidade de conflitos e arestas).
- Lista de relacionamentos legíveis no formato "Usuário → Filmes assistidos".
- Editor integrado para montar novos grafos bipartidos e salvar/visualizar o
  resultado instantaneamente.

## Uso como biblioteca
Para importar os módulos diretamente em um REPL ou script, você pode usar o
pacote `grafo` exposto na raiz ou adicionar o diretório `src/` ao `PYTHONPATH`:

```bash
# sem instalação prévia — o pacote raiz redireciona para src/grafo
python - <<'PY'
from grafo import GrafoBipartido, carregar_de_iteravel

grafo = GrafoBipartido()
grafo.carregar_de_iteravel([
    "Gabriel x Moana",
    "Larissa x Frozen",
])
print(grafo.verificar_biparticao().eh_bipartido)
PY

# se preferir manipular o PYTHONPATH manualmente
export PYTHONPATH="$(pwd)/src"
python - <<'PY'
from grafo import GrafoBipartido, carregar_de_arquivo

grafo = GrafoBipartido()
grafo.carregar_de_arquivo("exemplos/bipartido.txt")
print(grafo.verificar_biparticao().eh_bipartido)
PY
```

Também é possível instalar localmente com `pip install -e .` caso você mantenha um `pyproject.toml` ou outro arquivo de empacotamento.

## Testes automatizados
Execute `pytest` para validar os comportamentos principais do grafo e dos parsers. Os testes cobrem a leitura de arquivos de exemplo, o algoritmo de bipartição e o rastreamento de passos utilizado nas animações.
