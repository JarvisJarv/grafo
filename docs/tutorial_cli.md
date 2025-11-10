# Guia rápido: executando a CLI passo a passo

Este guia mostra, na prática, como usar o verificador de grafo bipartido com os exemplos de pessoas e filmes que acompanham o repositório. Use-o como roteiro quando quiser demonstrar o algoritmo ou apenas validar um novo arquivo `.txt` que você montou.

## 1. Preparar o ambiente
1. (Opcional, mas recomendado) crie um ambiente virtual: `python -m venv .venv && source .venv/bin/activate`.
2. Instale as dependências necessárias:
   ```bash
   pip install -r requirements.txt
   ```

## 2. Estrutura básica do comando
O programa principal fica em `src/main.py` e pode ser executado de duas formas equivalentes:

```bash
python -m src.main CAMINHO/DO/ARQUIVO.txt [OPÇÕES]
# ou
python src/main.py CAMINHO/DO/ARQUIVO.txt [OPÇÕES]
```

Basta substituir `CAMINHO/DO/ARQUIVO.txt` por um dos arquivos dentro de `exemplos/` ou por um arquivo seu.

## 3. Rodando o primeiro exemplo
Teste rápido com um grafo bipartido de usuários e filmes:

```bash
python -m src.main exemplos/usuario_filme_equilibrado.txt
```

A saída textual indica se o grafo é bipartido, quais vértices ficaram em cada partição e lista possíveis conflitos.

## 4. Entendendo cada opção
Todas as opções são adicionais ao caminho do arquivo. Você pode combiná-las livremente.

| Opção | Para que serve | Exemplo de uso |
|-------|----------------|----------------|
| `--json` | Imprime o resultado completo em JSON (bom para integrar com outras ferramentas). | `python -m src.main exemplos/usuario_filme_equilibrado.txt --json` |
| `--plot` | Abre uma janela com o grafo desenhado, destacando partições e conflitos. Requer `matplotlib` e `networkx`. | `python -m src.main exemplos/usuario_filme_equilibrado.txt --plot` |
| `--animar` | Mostra uma animação passo a passo da BFS que colore o grafo. | `python -m src.main exemplos/nao_bipartido.txt --animar` |
| `--exportar-animacao CAMINHO` | Gera um GIF ou MP4 com a mesma animação do `--animar`. Use com ou sem `--animar`. | `python -m src.main exemplos/nao_bipartido.txt --exportar-animacao docs/imagens/demo.gif` |
| `--layout {spring,circular,kamada_kawai,bipartido,flechas}` | Escolhe o layout do desenho. `spring` é o padrão; `flechas` agrupa as partições em ovais destacadas. | `python -m src.main exemplos/usuario_filme_equilibrado.txt --plot --layout flechas` |
| `--fps N` | Ajusta a velocidade da animação/exportação. Use um número maior para acelerar. | `python -m src.main exemplos/nao_bipartido.txt --animar --fps 3` |

> 💡 **Dica:** se `--plot` ou `--animar` avisarem que `matplotlib`/`networkx` não estão instalados, rode `pip install matplotlib networkx` dentro do seu ambiente virtual.

## 5. Combinações úteis
* Visualizar e exportar a animação ao mesmo tempo:
  ```bash
  python -m src.main exemplos/nao_bipartido.txt --animar --exportar-animacao docs/imagens/nao-bipartido.mp4 --fps 2
  ```
* Apenas gerar o arquivo animado (sem abrir janela):
  ```bash
  python -m src.main exemplos/usuario_filme_tendencias.txt --exportar-animacao docs/imagens/tendencias.gif
  ```

## 6. Próximos passos
Depois de testar com os exemplos, substitua o arquivo por um `.txt` seu contendo os pares `pessoa filme` que deseja avaliar. Se aparecerem conflitos, revise as conexões que ligam vértices do mesmo tipo — são elas que quebram a bipartição e indicam inconsistências nas recomendações.
