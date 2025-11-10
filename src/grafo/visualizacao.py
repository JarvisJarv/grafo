"""Rotinas de visualização de grafos usando matplotlib e networkx."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import networkx as nx

from .bipartido import GrafoBipartido, PassoBiparticao, ResultadoBiparticao

try:  # pragma: no cover - import opcional na ausência do matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter
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


def _calcular_posicoes_bipartido(resultado: ResultadoBiparticao) -> Posicoes:
    """Gera um layout em duas colunas para grafos bipartidos."""

    particao_a, particao_b = (sorted(particao) for particao in resultado.particoes)
    posicoes: Posicoes = {}

    if not particao_a and not particao_b:
        return posicoes

    altura_a = max(len(particao_a) - 1, 1)
    altura_b = max(len(particao_b) - 1, 1)

    for indice, vertice in enumerate(particao_a):
        if len(particao_a) <= 1:
            y = 0.5
        else:
            y = 1 - indice / altura_a
        posicoes[vertice] = (0.1, y)

    for indice, vertice in enumerate(particao_b):
        if len(particao_b) <= 1:
            y = 0.5
        else:
            y = 1 - indice / altura_b
        posicoes[vertice] = (0.9, y)

    return posicoes


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


def _cores_vertices_passo(grafo_nx: nx.Graph, passo: PassoBiparticao) -> List[str]:
    cores_visuais = {0: "tab:blue", 1: "tab:orange"}
    fila_conjunto = set(passo.fila)
    cores_vertices: List[str] = []
    for vertice in grafo_nx.nodes:
        cor = cores_visuais.get(passo.cores.get(vertice), "tab:gray")
        if vertice in fila_conjunto:
            cor = "mediumpurple"
        if vertice == passo.vertice_atual:
            cor = "tab:green"
        cores_vertices.append(cor)
    return cores_vertices


def _cores_arestas_passo(grafo_nx: nx.Graph, passo: PassoBiparticao) -> List[str]:
    conflitos = {tuple(sorted(aresta)) for aresta in passo.conflitos}
    aresta_atual = tuple(sorted(passo.aresta_analisada)) if passo.aresta_analisada else None
    cores: List[str] = []
    for origem, destino in grafo_nx.edges:
        aresta = tuple(sorted((origem, destino)))
        if aresta == aresta_atual:
            cores.append("tab:green")
        elif aresta in conflitos:
            cores.append("red")
        else:
            cores.append("0.65")
    return cores


def _formatar_texto_passo(passo: PassoBiparticao) -> str:
    fila = ", ".join(passo.fila) or "∅"
    conflitos = ", ".join(" -- ".join(aresta) for aresta in passo.conflitos) or "Nenhum"
    return "\n".join(
        [
            passo.descricao,
            f"Fila: [{fila}]",
            f"Conflitos: {conflitos}",
        ]
    )


def preparar_desenho(
    grafo: GrafoBipartido, *, layout: str = "spring"
) -> Tuple[nx.Graph, Posicoes, List[str], List[str], ResultadoBiparticao]:
    """Prepara os elementos necessários para desenhar um grafo."""

    layout = layout.lower()
    resultado = _obter_resultado(grafo)
    grafo_nx = _construir_grafo_networkx(grafo)

    posicoes: Posicoes = {}
    posicoes_definidas = grafo.posicoes
    if posicoes_definidas:
        posicoes.update({vertice: posicoes_definidas[vertice] for vertice in grafo_nx.nodes if vertice in posicoes_definidas})

    faltantes = [vertice for vertice in grafo_nx.nodes if vertice not in posicoes]
    if faltantes:
        if layout == "bipartido" and resultado.eh_bipartido:
            posicoes_calculadas = _calcular_posicoes_bipartido(resultado)
        else:
            subgrafo = grafo_nx.subgraph(faltantes).copy()
            posicoes_calculadas = _calcular_posicoes(subgrafo, layout)
        posicoes.update({vertice: posicoes_calculadas.get(vertice, (0.0, 0.0)) for vertice in faltantes})

    cores_por_vertice = _cores_vertices(resultado)
    cores_vertices = [cores_por_vertice.get(vertice, "tab:gray") for vertice in grafo_nx.nodes]
    cores_arestas = list(_cores_arestas_lista(grafo_nx.edges, resultado))

    return grafo_nx, posicoes, cores_vertices, cores_arestas, resultado


def exibir_grafo(
    grafo: GrafoBipartido,
    *,
    layout: str = "spring",
    titulo: str | None = None,
    mostrar_legenda: bool = True,
    mostrar: bool = True,
    caminho_saida: str | Path | None = None,
) -> None:
    """Renderiza o grafo destacando as partições e conflitos."""

    grafo_nx, posicoes, cores_vertices, cores_arestas, resultado = preparar_desenho(
        grafo, layout=layout
    )

    fig, eixo = plt.subplots(figsize=(8, 6))
    nx.draw_networkx_edges(grafo_nx, posicoes, ax=eixo, edge_color=cores_arestas, width=2)
    nx.draw_networkx_nodes(
        grafo_nx,
        posicoes,
        ax=eixo,
        node_color=cores_vertices,
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

    if caminho_saida is not None:
        caminho = Path(caminho_saida)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(caminho, dpi=150)

    if mostrar:
        plt.show()
    else:
        plt.close(fig)


def exibir_grafo_de_arquivo(caminho: str | Path, **kwargs) -> None:
    """Carrega um grafo de ``caminho`` e exibe a visualização."""

    grafo = GrafoBipartido()
    grafo.carregar_de_arquivo(str(caminho))
    grafo.verificar_biparticao()
    exibir_grafo(grafo, **kwargs)


def animar_verificacao(
    grafo: GrafoBipartido,
    *,
    layout: str = "spring",
    titulo: str | None = None,
    mostrar: bool = True,
    caminho_saida: str | Path | None = None,
    fps: int = 1,
    intervalo_ms: int = 1000,
) -> FuncAnimation:
    """Cria uma animação destacando as etapas da verificação do grafo."""

    resultado, passos = grafo.verificar_biparticao_com_passos()
    grafo_nx, posicoes, _, _, _ = preparar_desenho(grafo, layout=layout)

    fig, eixo = plt.subplots(figsize=(8, 6))
    colecao_arestas = nx.draw_networkx_edges(grafo_nx, posicoes, ax=eixo, width=2)
    colecao_vertices = nx.draw_networkx_nodes(
        grafo_nx,
        posicoes,
        ax=eixo,
        node_color=_cores_vertices_passo(grafo_nx, passos[0]) if passos else "tab:gray",
        node_size=900,
        linewidths=1.5,
        edgecolors="black",
    )
    nx.draw_networkx_labels(grafo_nx, posicoes, ax=eixo, font_weight="bold")

    eixo.set_axis_off()

    if titulo:
        eixo.set_title(titulo)

    particao_a, particao_b = resultado.particoes
    elementos_legenda = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="tab:blue", label=f"Partição 0 ({len(particao_a)})"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="tab:orange", label=f"Partição 1 ({len(particao_b)})"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="tab:green", label="Processando"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="mediumpurple", label="Fila"),
        plt.Line2D([0], [0], color="red", lw=2, label="Conflito"),
    ]
    eixo.legend(handles=elementos_legenda, loc="upper right")

    texto_info = eixo.text(
        0.02,
        0.98,
        _formatar_texto_passo(passos[0]) if passos else "",
        transform=eixo.transAxes,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.9),
    )

    plt.tight_layout()

    def atualizar(indice: int) -> Sequence[object]:
        passo = passos[indice]
        cores_vertices = _cores_vertices_passo(grafo_nx, passo)
        colecao_vertices.set_color(cores_vertices)
        cores_arestas = _cores_arestas_passo(grafo_nx, passo)
        colecao_arestas.set_color(cores_arestas)
        texto_info.set_text(_formatar_texto_passo(passo))
        if titulo:
            eixo.set_title(f"{titulo} — etapa {indice + 1}/{len(passos)}")
        return colecao_vertices, colecao_arestas, texto_info

    animacao = FuncAnimation(
        fig,
        atualizar,
        frames=len(passos),
        interval=max(1, intervalo_ms),
        repeat=False,
    )

    if caminho_saida:
        caminho = Path(caminho_saida)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        extensao = caminho.suffix.lower()
        try:
            if extensao == ".gif":
                writer: PillowWriter | FFMpegWriter = PillowWriter(fps=fps)
            elif extensao == ".mp4":
                writer = FFMpegWriter(fps=fps)
            else:
                writer = PillowWriter(fps=fps) if extensao in {"", ".gif"} else FFMpegWriter(fps=fps)
            animacao.save(str(caminho), writer=writer)
        except Exception as exc:  # pragma: no cover - dependente do ambiente
            plt.close(fig)
            raise RuntimeError(f"Falha ao exportar animação para {caminho}: {exc}") from exc

    if mostrar:
        plt.show()
    else:
        plt.close(fig)

    return animacao

