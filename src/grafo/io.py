"""Utilitários para leitura de grafos em arquivos texto."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Set, Tuple


@dataclass(frozen=True)
class DadosGrafo:
    """Estrutura de dados simples para representar vértices, arestas e posições."""

    vertices: Set[str]
    arestas: List[Tuple[str, str]]
    posicoes: dict[str, Tuple[float, float]]


def _normalizar_linha(linha: str) -> str:
    """Remove comentários e espaços excedentes de uma linha."""

    conteudo = linha.split("#", 1)[0].strip()
    return conteudo


def carregar_de_arquivo(caminho: str | Path) -> DadosGrafo:
    """Lê um arquivo texto contendo a descrição de um grafo.

    O formato aceito é compatível com ``carregar_de_iteravel`` e permite o uso
    opcional da seção ``[vertices]`` antes da listagem das arestas.
    """

    path = Path(caminho)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    with path.open("r", encoding="utf-8") as arquivo:
        return carregar_de_iteravel(arquivo)


def carregar_de_iteravel(linhas: Iterable[str]) -> DadosGrafo:
    """Permite carregar dados de um iterável de strings em memória.

    O conteúdo pode ser dividido em duas seções explícitas:

    ``[vertices]``
        Lista de vértices. Cada linha deve começar pelo identificador e pode
        incluir atributos no formato ``chave=valor``. A posição do vértice pode
        ser informada com ``pos=x,y`` ou com os pares ``x=<float>`` e
        ``y=<float>``.

    ``[arestas]``
        Lista de arestas não direcionadas. Cada linha deve conter exatamente
        dois identificadores separados por espaço.

    Caso a seção ``[vertices]`` não seja fornecida, as linhas são interpretadas
    diretamente como arestas (mantendo compatibilidade com o formato antigo).
    """

    vertices: Set[str] = set()
    arestas: List[Tuple[str, str]] = []
    posicoes: dict[str, Tuple[float, float]] = {}
    coordenadas_parciais: dict[str, dict[str, float]] = {}

    secao = "arestas"

    for numero_linha, linha in enumerate(linhas, start=1):
        conteudo = _normalizar_linha(linha)
        if not conteudo:
            continue

        if conteudo.startswith("[") and conteudo.endswith("]"):
            secao = conteudo.strip("[] ").lower()
            if secao not in {"vertices", "arestas"}:
                raise ValueError(
                    "Seção desconhecida na linha "
                    f"{numero_linha}: use [vertices] ou [arestas]"
                )
            continue

        if secao == "vertices":
            partes = conteudo.split()
            identificador = partes[0]
            vertices.add(identificador)

            for atributo in partes[1:]:
                if "=" not in atributo:
                    raise ValueError(
                        "Formato inválido na linha "
                        f"{numero_linha}: atributos devem usar a forma chave=valor"
                    )

                chave, valor = atributo.split("=", 1)
                chave = chave.strip().lower()
                valor = valor.strip()

                if chave == "pos":
                    try:
                        x_str, y_str = valor.split(",", 1)
                        posicoes[identificador] = (float(x_str), float(y_str))
                    except ValueError as exc:  # pragma: no cover - validação simples
                        raise ValueError(
                            "Formato inválido na linha "
                            f"{numero_linha}: esperado pos=x,y"
                        ) from exc
                elif chave in {"x", "y"}:
                    try:
                        coordenadas = coordenadas_parciais.setdefault(identificador, {})
                        coordenadas[chave] = float(valor)
                        if {"x", "y"} <= coordenadas.keys():
                            posicoes[identificador] = (coordenadas["x"], coordenadas["y"])
                    except ValueError as exc:  # pragma: no cover - validação simples
                        raise ValueError(
                            "Formato inválido na linha "
                            f"{numero_linha}: valores de x/y devem ser numéricos"
                        ) from exc

            continue

        partes = conteudo.split()
        if len(partes) == 3 and partes[1].lower() == "x":
            origem, destino = partes[0], partes[2]
        elif len(partes) == 2:
            origem, destino = partes
        else:
            raise ValueError(
                "Formato inválido na linha "
                f"{numero_linha}: use 'origem destino' ou 'origem x destino'"
            )

        vertices.update((origem, destino))
        arestas.append((origem, destino))

    return DadosGrafo(vertices=vertices, arestas=arestas, posicoes=posicoes)
