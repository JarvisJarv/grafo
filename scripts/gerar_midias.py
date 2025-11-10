"""Gera capturas e animações da visualização do grafo bipartido."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Dict, Iterable, List, Sequence, Tuple

import matplotlib

# Backend "Agg" evita a necessidade de um display durante a geração das figuras.
matplotlib.use("Agg")

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import networkx as nx

# Garante que ``import grafo`` funcione mesmo sem instalar o pacote.
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR / "src"))

from grafo.bipartido import GrafoBipartido


Cor = int
Aresta = Tuple[str, str]


@dataclass
class QuadroAnimacao:
    """Estado intermediário utilizado para montar a animação."""

    descricao: str
    cores: Dict[str, Cor]
    conflitos: Sequence[Aresta]


def _carregar_grafo(caminho: Path) -> Tuple[GrafoBipartido, nx.Graph]:
    grafo = GrafoBipartido()
    grafo.carregar_de_arquivo(str(caminho))
    grafo.verificar_biparticao()
    grafo_nx = nx.Graph()
    grafo_nx.add_nodes_from(sorted(grafo.vertices))
    grafo_nx.add_edges_from(sorted(grafo.arestas))
    return grafo, grafo_nx


def _cores_vertices(cores: Dict[str, Cor], vertices: Iterable[str]) -> List[str]:
    paleta = {0: "tab:blue", 1: "tab:orange"}
    return [paleta.get(cores.get(vertice), "tab:gray") for vertice in vertices]


def _cores_arestas(arestas: Iterable[Aresta], conflitos: Iterable[Aresta]) -> List[str]:
    conflitos_normalizados = {tuple(sorted(aresta)) for aresta in conflitos}
    return ["red" if tuple(sorted(aresta)) in conflitos_normalizados else "0.65" for aresta in arestas]


def gerar_captura_estatica(caminho_grafo: Path, destino: Path, *, layout: str = "spring") -> None:
    """Gera uma imagem estática do grafo com a coloração final."""

    grafo, grafo_nx = _carregar_grafo(caminho_grafo)
    posicoes = _calcular_posicoes(grafo_nx, layout)
    resultado = grafo.resultado
    assert resultado is not None

    fig, eixo = plt.subplots(figsize=(8, 6))
    nx.draw_networkx_edges(
        grafo_nx,
        posicoes,
        ax=eixo,
        edge_color=_cores_arestas(grafo_nx.edges, resultado.conflitos),
        width=2,
    )
    nx.draw_networkx_nodes(
        grafo_nx,
        posicoes,
        ax=eixo,
        node_color=_cores_vertices(resultado.cores, grafo_nx.nodes),
        node_size=900,
        linewidths=1.5,
        edgecolors="black",
    )
    nx.draw_networkx_labels(grafo_nx, posicoes, ax=eixo, font_weight="bold")
    eixo.set_axis_off()
    eixo.set_title("Coloração final: grafo bipartido")
    plt.tight_layout()
    fig.savefig(destino, dpi=150)
    plt.close(fig)


def _calcular_posicoes(grafo_nx: nx.Graph, layout: str) -> Dict[str, Tuple[float, float]]:
    layout = layout.lower()
    if layout == "circular":
        return nx.circular_layout(grafo_nx)
    if layout in {"kamada", "kamada_kawai", "kk"}:
        return nx.kamada_kawai_layout(grafo_nx)
    return nx.spring_layout(grafo_nx, seed=42)


def _passos_bfs(grafo: GrafoBipartido) -> List[QuadroAnimacao]:
    """Executa o BFS do grafo registrando estados intermediários."""

    cores: Dict[str, Cor] = {}
    conflitos: List[Aresta] = []
    quadros: List[QuadroAnimacao] = [
        QuadroAnimacao("Início: nenhum vértice colorido", cores={}, conflitos=tuple()),
    ]

    adjacencia = {vertice: set() for vertice in grafo.vertices}
    for origem, destino in grafo.arestas:
        adjacencia.setdefault(origem, set()).add(destino)
        adjacencia.setdefault(destino, set()).add(origem)

    from collections import deque

    for vertice in sorted(grafo.vertices):
        if vertice in cores:
            continue

        cores[vertice] = 0
        quadros.append(
            QuadroAnimacao(
                f"Colorindo vértice inicial {vertice} com a cor 0",
                cores=dict(cores),
                conflitos=tuple(conflitos),
            )
        )
        fila: deque[str] = deque([vertice])

        while fila:
            atual = fila.popleft()
            cor_atual = cores[atual]
            cor_oposta = 1 - cor_atual

            for vizinho in sorted(adjacencia.get(atual, set())):
                if vizinho not in cores:
                    cores[vizinho] = cor_oposta
                    fila.append(vizinho)
                    quadros.append(
                        QuadroAnimacao(
                            f"Colorindo {vizinho} com a cor {cor_oposta} a partir de {atual}",
                            cores=dict(cores),
                            conflitos=tuple(conflitos),
                        )
                    )
                elif cores[vizinho] == cor_atual:
                    conflito = tuple(sorted((atual, vizinho)))
                    if conflito not in conflitos:
                        conflitos.append(conflito)
                        quadros.append(
                            QuadroAnimacao(
                                f"Conflito detectado em {conflito[0]} — {conflito[1]}",
                                cores=dict(cores),
                                conflitos=tuple(conflitos),
                            )
                        )

    quadros.append(
        QuadroAnimacao(
            "Resultado final após o BFS", cores=dict(cores), conflitos=tuple(conflitos)
        )
    )
    return quadros


def gerar_animacao_coloracao(
    caminho_grafo: Path,
    destino: Path,
    *,
    layout: str = "spring",
    intervalo_ms: int = 1200,
) -> None:
    """Gera uma animação GIF mostrando o processo de coloração passo a passo."""

    grafo, grafo_nx = _carregar_grafo(caminho_grafo)
    posicoes = _calcular_posicoes(grafo_nx, layout)
    quadros = _passos_bfs(grafo)

    fig, eixo = plt.subplots(figsize=(8, 6))

    def desenhar(quadro: QuadroAnimacao) -> None:
        eixo.clear()
        nx.draw_networkx_edges(
            grafo_nx,
            posicoes,
            ax=eixo,
            edge_color=_cores_arestas(grafo_nx.edges, quadro.conflitos),
            width=2,
        )
        nx.draw_networkx_nodes(
            grafo_nx,
            posicoes,
            ax=eixo,
            node_color=_cores_vertices(quadro.cores, grafo_nx.nodes),
            node_size=900,
            linewidths=1.5,
            edgecolors="black",
        )
        nx.draw_networkx_labels(grafo_nx, posicoes, ax=eixo, font_weight="bold")
        eixo.set_axis_off()
        eixo.set_title("Passo a passo da coloração (BFS)")
        eixo.text(
            0.02,
            0.98,
            quadro.descricao,
            transform=eixo.transAxes,
            va="top",
            ha="left",
            fontsize=11,
        )

    fps = max(1, 1000 // max(intervalo_ms, 1))
    writer = animation.PillowWriter(fps=fps)

    with writer.saving(fig, str(destino), dpi=100):
        for quadro in quadros:
            desenhar(quadro)
            writer.grab_frame()
    plt.close(fig)


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    pasta_imagens = base / "docs" / "imagens"
    pasta_imagens.mkdir(parents=True, exist_ok=True)

    grafo_bipartido = base / "exemplos" / "bipartido.txt"
    grafo_nao_bipartido = base / "exemplos" / "nao_bipartido.txt"

    gerar_captura_estatica(
        grafo_bipartido,
        pasta_imagens / "visualizacao_bipartido.png",
        layout="spring",
    )
    gerar_animacao_coloracao(
        grafo_nao_bipartido,
        pasta_imagens / "animacao_coloracao.gif",
        layout="spring",
    )


if __name__ == "__main__":
    main()
