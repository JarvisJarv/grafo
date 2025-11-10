# Projeto de Verificação de Grafo Bipartido

Este repositório reúne os artefatos desenvolvidos para o estudo de grafos bipartidos usando a relação Usuários × Filmes como cenário principal. Todo o material está organizado de forma que qualquer pessoa possa reproduzir o algoritmo, visualizar sua execução e estudar os resultados.

## Entregáveis técnicos (trabalho)
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
2. Rode o verificador com um arquivo de exemplo: `python -m src.main exemplos/usuario_filme_bipartido.txt --plot`.
3. Para exportar uma animação: `python -m src.main exemplos/usuario_filme_bipartido.txt --animar --exportar-animacao docs/imagens/biparticao.gif`.

## Testes automatizados
Execute `pytest` para validar os comportamentos principais do grafo e dos parsers.
