"""Utilitários para leitura de grafos em arquivos texto."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Set, Tuple


@dataclass(frozen=True)
class DadosGrafo:
    """Estrutura de dados simples para representar vértices e arestas."""

    vertices: Set[str]
    arestas: List[Tuple[str, str]]


def _normalizar_linha(linha: str) -> str:
    """Remove comentários e espaços excedentes de uma linha."""

    conteudo = linha.split("#", 1)[0].strip()
    return conteudo


def carregar_de_arquivo(caminho: str | Path) -> DadosGrafo:
    """Lê um arquivo texto contendo arestas e retorna os dados do grafo.

    Cada linha válida do arquivo deve conter dois rótulos de vértice separados
    por espaço ou tabulação, representando uma aresta não direcionada.
    Linhas em branco ou iniciadas por ``#`` são ignoradas.
    """

    path = Path(caminho)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    vertices: Set[str] = set()
    arestas: List[Tuple[str, str]] = []

    with path.open("r", encoding="utf-8") as arquivo:
        for numero_linha, linha in enumerate(arquivo, start=1):
            conteudo = _normalizar_linha(linha)
            if not conteudo:
                continue

            partes = conteudo.split()
            if len(partes) != 2:
                raise ValueError(
                    "Formato inválido na linha "
                    f"{numero_linha}: esperado dois vértices separados por espaço"
                )

            origem, destino = partes
            vertices.update((origem, destino))
            arestas.append((origem, destino))

    return DadosGrafo(vertices=vertices, arestas=arestas)


def carregar_de_iteravel(linhas: Iterable[str]) -> DadosGrafo:
    """Permite carregar dados de um iterável de strings em memória."""

    vertices: Set[str] = set()
    arestas: List[Tuple[str, str]] = []

    for numero_linha, linha in enumerate(linhas, start=1):
        conteudo = _normalizar_linha(linha)
        if not conteudo:
            continue

        partes = conteudo.split()
        if len(partes) != 2:
            raise ValueError(
                "Formato inválido na linha "
                f"{numero_linha}: esperado dois vértices separados por espaço"
            )

        origem, destino = partes
        vertices.update((origem, destino))
        arestas.append((origem, destino))

    return DadosGrafo(vertices=vertices, arestas=arestas)
