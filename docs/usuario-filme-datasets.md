# Conjuntos de dados Usuário–Filme

Dois arquivos de exemplo estão disponíveis em `exemplos/usuario_filme_equilibrado.txt` e
`exemplos/usuario_filme_tendencias.txt`. Eles representam grafos bipartidos entre
usuários e filmes com características distintas (preferências complementares e gostos
populares concentrados, respectivamente).

## Formato do arquivo

Cada arquivo segue um formato textual dividido em duas seções:

```
[vertices]
<identificador> [pos=x,y | x=<float> y=<float>] [outros_atributos]
[arestas]
<identificador_origem> <identificador_destino>
```

- As linhas iniciadas com `#` são tratadas como comentários.
- A seção `[vertices]` é opcional, mas quando presente permite declarar atributos para
  cada vértice antes das arestas.
  - O primeiro campo é sempre o identificador único do vértice.
  - É possível informar a posição do vértice usando `pos=x,y` ou os pares
    `x=<float>` e `y=<float>`. Os valores são opcionais e aceitam ponto decimal.
  - Atributos adicionais no formato `chave=valor` são ignorados pela aplicação, mas
    podem ser usados para documentação.
- A seção `[arestas]` lista as conexões entre vértices. Cada linha deve conter dois
  identificadores separados por espaço, representando uma aresta não direcionada.

Caso a seção `[vertices]` não seja fornecida, o arquivo pode conter apenas a seção de
arestas (mantendo compatibilidade com exemplos anteriores).

## Características dos conjuntos

- `usuario_filme_equilibrado.txt` apresenta pares de usuários com preferências
  complementares por filmes de gêneros distintos, resultando em um grafo equilibrado.
- `usuario_filme_tendencias.txt` concentra vários usuários em títulos populares,
  gerando um grafo mais denso em torno de poucos filmes e demonstrando o uso de
  posições opcionais apenas para parte dos vértices.
