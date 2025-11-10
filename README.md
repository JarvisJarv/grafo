# Projeto de Verificação de Grafo Bipartido

Este repositório reúne os artefatos desenvolvidos para o estudo de grafos bipartidos usando a relação Usuários × Filmes como cenário principal. Todo o material está organizado de forma que qualquer pessoa possa reproduzir o algoritmo, visualizar sua execução e estudar os resultados.

## Estrutura geral
- `src/`: código-fonte do verificador, leitor de arquivos texto e utilidades de visualização.
- `exemplos/`: coleções de arquivos `.txt` que definem os grafos utilizados nos testes e demonstrações.
- `docs/`: documentação técnica do trabalho, materiais de apresentação e guia de estudos.
- `scripts/`: automações para gerar animações, capturas e demais mídias de apoio.
- `tests/`: cenários automatizados garantindo a compatibilidade dos parsers e da coleta de passos do algoritmo.

## Requisitos
- Python 3.11+
- Dependências opcionais para visualização: `matplotlib` e `networkx` (instale com `pip install -r requirements.txt`).

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
1. (Opcional) Crie um ambiente virtual e instale as dependências: `pip install -r requirements.txt`.
2. Escolha um arquivo de entrada em `exemplos/`. Existem variantes como `bipartido.txt`, `usuario_filme_equilibrado.txt` e `usuario_filme_tendencias.txt` (o antigo `usuario_filme_bipartido.txt` continua compatível caso esteja no seu diretório local).
3. No terminal (PowerShell no Windows ou bash no Linux/macOS), execute um dos comandos abaixo para rodar o verificador:
   - usando o módulo: `python -m src.main exemplos/bipartido.txt`
   - executando diretamente: `python src/main.py exemplos/bipartido.txt`
   - exibindo o relatório completo em JSON: `python -m src.main exemplos/nao_bipartido.txt --json`
   - comando legado (caso esteja usando o arquivo antigo): `python -m src.main exemplos/usuario_filme_bipartido.txt --plot`
4. Para visualizar ou animar a execução:
   - Visualização estática: acrescente `--plot` aos comandos anteriores (ex.: `python -m src.main exemplos/bipartido.txt --plot`).
   - Animação passo a passo: `python -m src.main exemplos/nao_bipartido.txt --animar`.
   - Exportar mídia: `python -m src.main exemplos/nao_bipartido.txt --animar --exportar-animacao docs/imagens/biparticao.gif`.

### Teste rápido com Usuários × Filmes
Para validar especificamente a relação de recomendação Usuário × Filme:

```powershell
python -m src.main exemplos/usuario_filme_equilibrado.txt --json
```

O comando acima lê o arquivo de texto, verifica a bipartição entre pessoas e filmes e exibe as duas partições, além de conflitos (se existirem). Também é possível acrescentar `--plot` ou `--animar` para inspecionar visualmente o grafo.

## Geração de mídias automáticas
Execute `python scripts/gerar_midias.py` para produzir capturas e animações utilizadas na apresentação. Os arquivos são salvos em `docs/imagens/` (pasta ignorada pelo Git).

## Testes automatizados
Execute `pytest` para validar os comportamentos principais do grafo e dos parsers.
