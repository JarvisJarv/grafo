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

## Como executar
1. Instale as dependências: `pip install -r requirements.txt`.
2. Escolha um arquivo de entrada em `exemplos/`. Existem variantes como `bipartido.txt`, `usuario_filme_equilibrado.txt` e `usuario_filme_tendencias.txt`. O arquivo legado `usuario_filme_bipartido.txt` continua compatível caso esteja no seu diretório local.
3. Rode o verificador com um arquivo de exemplo:
   - usando o módulo: `python -m src.main exemplos/bipartido.txt --plot`
   - executando diretamente: `python src/main.py exemplos/bipartido.txt --plot`
   - comando legado (caso esteja usando o arquivo antigo): `python -m src.main exemplos/usuario_filme_bipartido.txt --plot`
4. Para exportar uma animação: `python -m src.main exemplos/nao_bipartido.txt --animar --exportar-animacao docs/imagens/biparticao.gif`.

### Opções da CLI
- `--json`: imprime o resultado completo (partições, conflitos e posições) em formato JSON.
- `--plot`: abre uma visualização estática destacando as partições e conflitos.
- `--animar`: executa a animação dos passos do algoritmo.
- `--exportar-animacao CAMINHO`: salva a animação em GIF ou MP4 para o caminho informado.
- `--layout {spring,circular,kamada_kawai}`: escolhe o algoritmo de posicionamento dos vértices.
- `--fps N`: define a taxa de quadros da animação ou exportação (valor mínimo 1).

## Uso como biblioteca
Para importar os módulos diretamente em um REPL ou script, adicione o diretório `src/` ao `PYTHONPATH`:

```bash
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
