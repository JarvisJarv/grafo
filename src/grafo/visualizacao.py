"""Rotinas de visualização de grafos usando matplotlib e networkx."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Tuple

import networkx as nx

from .bipartido import GrafoBipartido, ResultadoBiparticao

try:  # pragma: no cover - import opcional na ausência do matplotlib
    import matplotlib.pyplot as plt
except ImportError as exc:  # pragma: no cover - tratado pelo chamador
    raise

Posicoes = Dict[str, Tuple[float, float]]


def _calcular_posicoes(grafo_nx: nx.Graph, layout: str) -> Posicoes:
    """Calcula a posição dos vértices conforme o layout desejado."""

    layout = layout.lower()
    if layout == "circular":
        return nx.circular_layout(grafo_nx)
    if layout in {"kamada", "kamada_kawai", "kk"}:
        return nx.kamada_kawai_layout(grafo_nx)
    if layout == "planar":
        try:
            return nx.planar_layout(grafo_nx)
        except nx.NetworkXException:
            pass
    return nx.spring_layout(grafo_nx, seed=42)


def _construir_grafo_networkx(grafo: GrafoBipartido) -> nx.Graph:
    """Converte ``GrafoBipartido`` para ``networkx.Graph``."""

    grafo_nx = nx.Graph()
    grafo_nx.add_nodes_from(sorted(grafo.vertices))
    grafo_nx.add_edges_from(sorted(grafo.arestas))
    return grafo_nx


def _obter_resultado(grafo: GrafoBipartido) -> ResultadoBiparticao:
    """Garante que o resultado de bipartição esteja disponível."""

    if grafo.resultado is None:
        return grafo.verificar_biparticao()
    return grafo.resultado


def _cores_vertices(resultado: ResultadoBiparticao) -> Dict[str, str]:
    """Mapeia vértices para cores visuais baseadas na partição."""

    cores_visuais = {0: "tab:blue", 1: "tab:orange"}
    return {vertice: cores_visuais.get(cor, "tab:gray") for vertice, cor in resultado.cores.items()}


def _cores_arestas_lista(arestas: Iterable[Tuple[str, str]], resultado: ResultadoBiparticao) -> Iterable[str]:
    conflitos = {tuple(sorted(aresta)) for aresta in resultado.conflitos}
    for aresta in arestas:
        yield "red" if tuple(sorted(aresta)) in conflitos else "0.65"


def exibir_grafo(
    grafo: GrafoBipartido,
    *,
    layout: str = "spring",
    titulo: str | None = None,
    mostrar_legenda: bool = True,
) -> None:
    """Renderiza o grafo destacando as partições e conflitos."""

    resultado = _obter_resultado(grafo)
    grafo_nx = _construir_grafo_networkx(grafo)
    posicoes = _calcular_posicoes(grafo_nx, layout)

    cores_vertices = _cores_vertices(resultado)
    cores_padrao_vertices = [cores_vertices.get(vertice, "tab:gray") for vertice in grafo_nx.nodes]
    cores_arestas = list(_cores_arestas_lista(grafo_nx.edges, resultado))

    fig, eixo = plt.subplots(figsize=(8, 6))
    nx.draw_networkx_edges(grafo_nx, posicoes, ax=eixo, edge_color=cores_arestas, width=2)
    nx.draw_networkx_nodes(
        grafo_nx,
        posicoes,
        ax=eixo,
        node_color=cores_padrao_vertices,
        node_size=900,
        linewidths=1.5,
        edgecolors="black",
    )
    nx.draw_networkx_labels(grafo_nx, posicoes, ax=eixo, font_weight="bold")

    eixo.set_axis_off()

    if titulo:
        eixo.set_title(titulo)

    if mostrar_legenda:
        particao_a, particao_b = resultado.particoes
        elementos_legenda = [
            plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="tab:blue", label=f"Partição 0 ({len(particao_a)})"),
            plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="tab:orange", label=f"Partição 1 ({len(particao_b)})"),
        ]
        if resultado.conflitos:
            elementos_legenda.append(
                plt.Line2D([0], [0], color="red", lw=2, label=f"Conflitos ({len(resultado.conflitos)})")
            )
        eixo.legend(handles=elementos_legenda, loc="upper right")

    plt.tight_layout()
    plt.show()


def exibir_grafo_de_arquivo(caminho: str | Path, **kwargs) -> None:
    """Carrega um grafo de ``caminho`` e exibe a visualização."""

    grafo = GrafoBipartido()
    grafo.carregar_de_arquivo(str(caminho))
    grafo.verificar_biparticao()
    exibir_grafo(grafo, **kwargs)

