"""Rotinas de visualização de grafos usando matplotlib e networkx."""
from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import networkx as nx

from .bipartido import GrafoBipartido, PassoBiparticao, ResultadoBiparticao

try:  # pragma: no cover - import opcional na ausência do matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter
    from matplotlib.widgets import Button
except ImportError as exc:  # pragma: no cover - tratado pelo chamador
    raise

Posicoes = Dict[str, Tuple[float, float]]

_ANIMACOES_ATIVAS: List[FuncAnimation] = []


def _registrar_animacao_ativa(figura: "plt.Figure", animacao: FuncAnimation) -> None:
    """Mantém referência às animações enquanto a janela estiver aberta."""

    _ANIMACOES_ATIVAS.append(animacao)

    def _remover_animacao(_event: object) -> None:
        try:
            _ANIMACOES_ATIVAS.remove(animacao)
        except ValueError:
            pass

    if figura.canvas is not None:
        figura.canvas.mpl_connect("close_event", _remover_animacao)


def _ajustar_limites_eixo(eixo: "plt.Axes", posicoes: Posicoes, margem: float = 0.15) -> None:
    """Garante espaço extra ao redor do grafo para evitar cortes em rótulos."""

    if not posicoes:
        return

    xs = [coord[0] for coord in posicoes.values()]
    ys = [coord[1] for coord in posicoes.values()]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    largura = max(max_x - min_x, 1e-3)
    altura = max(max_y - min_y, 1e-3)

    margem_x = largura * margem
    margem_y = altura * margem

    eixo.set_xlim(min_x - margem_x, max_x + margem_x)
    eixo.set_ylim(min_y - margem_y, max_y + margem_y)


def _deslocar_rotulos(posicoes: Posicoes, deslocamento: float = 0.085) -> Posicoes:
    """Move os rótulos ligeiramente para cima dos vértices."""

    return {vertice: (coord[0], coord[1] + deslocamento) for vertice, coord in posicoes.items()}


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

    particao_0, particao_1 = (sorted(resultado.particao(cor)) for cor in (0, 1))
    posicoes: Posicoes = {}

    if not particao_0 and not particao_1:
        return posicoes

    altura_0 = max(len(particao_0) - 1, 1)
    altura_1 = max(len(particao_1) - 1, 1)

    for indice, vertice in enumerate(particao_1):
        if len(particao_1) <= 1:
            y = 0.5
        else:
            y = 1 - indice / altura_1
        posicoes[vertice] = (0.1, y)

    for indice, vertice in enumerate(particao_0):
        if len(particao_0) <= 1:
            y = 0.5
        else:
            y = 1 - indice / altura_0
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
    layout_calculo = "bipartido" if layout in {"bipartido", "flechas"} else layout
    resultado = _obter_resultado(grafo)
    grafo_nx = _construir_grafo_networkx(grafo)

    posicoes: Posicoes = {}
    posicoes_definidas = grafo.posicoes
    if posicoes_definidas:
        posicoes.update({vertice: posicoes_definidas[vertice] for vertice in grafo_nx.nodes if vertice in posicoes_definidas})

    faltantes = [vertice for vertice in grafo_nx.nodes if vertice not in posicoes]
    if faltantes:
        if layout_calculo == "bipartido" and resultado.eh_bipartido:
            posicoes_calculadas = _calcular_posicoes_bipartido(resultado)
        else:
            subgrafo = grafo_nx.subgraph(faltantes).copy()
            posicoes_calculadas = _calcular_posicoes(subgrafo, layout_calculo)
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
    fig.patch.set_facecolor("#f8fafc")
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
    posicoes_rotulos = _deslocar_rotulos(posicoes)
    nx.draw_networkx_labels(
        grafo_nx,
        posicoes_rotulos,
        ax=eixo,
        font_weight="bold",
        verticalalignment="bottom",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.85),
    )

    _ajustar_limites_eixo(eixo, posicoes_rotulos)

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

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            "This figure includes Axes that are not compatible with tight_layout",
            UserWarning,
        )
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
    intervalo_ms: int = 600,
) -> FuncAnimation:
    """Cria uma animação destacando as etapas da verificação do grafo."""

    resultado, passos = grafo.verificar_biparticao_com_passos()
    grafo_nx, posicoes, _, _, _ = preparar_desenho(grafo, layout=layout)

    fig = plt.figure(figsize=(12, 7))
    grade = fig.add_gridspec(
        2,
        2,
        height_ratios=[3.5, 1.0],
        width_ratios=[3.6, 1.6],
        hspace=0.35,
        wspace=0.3,
    )
    eixo_grafo = fig.add_subplot(grade[0, 0])
    eixo_info = fig.add_subplot(grade[0, 1])
    eixo_legenda = fig.add_subplot(grade[1, :])
    fig.patch.set_facecolor("#f8fafc")
    eixo_info.set_facecolor("#e2e8f0")
    colecao_arestas = nx.draw_networkx_edges(grafo_nx, posicoes, ax=eixo_grafo, width=2)
    colecao_vertices = nx.draw_networkx_nodes(
        grafo_nx,
        posicoes,
        ax=eixo_grafo,
        node_color=_cores_vertices_passo(grafo_nx, passos[0]) if passos else "tab:gray",
        node_size=900,
        linewidths=1.5,
        edgecolors="black",
    )
    colecao_arestas.set_animated(True)
    colecao_vertices.set_animated(True)
    posicoes_rotulos = _deslocar_rotulos(posicoes)
    nx.draw_networkx_labels(
        grafo_nx,
        posicoes_rotulos,
        ax=eixo_grafo,
        font_weight="bold",
        verticalalignment="bottom",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.85),
    )

    _ajustar_limites_eixo(eixo_grafo, posicoes_rotulos)

    eixo_grafo.set_axis_off()

    if titulo:
        eixo_grafo.set_title(titulo)

    particao_a, particao_b = resultado.particoes
    elementos_legenda = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="tab:blue", label=f"Partição 0 ({len(particao_a)})"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="tab:orange", label=f"Partição 1 ({len(particao_b)})"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="tab:green", label="Processando"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="mediumpurple", label="Fila"),
        plt.Line2D([0], [0], color="red", lw=2, label="Conflito"),
    ]
    eixo_legenda.set_axis_off()
    eixo_legenda.legend(
        handles=elementos_legenda,
        loc="center",
        ncol=len(elementos_legenda),
        frameon=False,
    )

    eixo_info.set_axis_off()
    eixo_info.set_xlim(0, 1)
    eixo_info.set_ylim(0, 1)

    texto_info = eixo_info.text(
        0.5,
        0.5,
        _formatar_texto_passo(passos[0]) if passos else "",
        transform=eixo_info.transAxes,
        verticalalignment="center",
        horizontalalignment="center",
        wrap=True,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.95),
    )
    texto_info.set_animated(True)

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            "This figure includes Axes that are not compatible with tight_layout",
            UserWarning,
        )
        plt.tight_layout()

    intervalo_base = max(1, intervalo_ms)
    estado_animacao: dict[str, object] = {
        "indice_atual": 0,
        "pausado": False,
        "intervalo": float(intervalo_base),
        "intervalo_base": float(intervalo_base),
    }

    def atualizar(indice: int) -> Sequence[object]:
        passo = passos[indice]
        cores_vertices = _cores_vertices_passo(grafo_nx, passo)
        colecao_vertices.set_facecolor(cores_vertices)
        cores_arestas = _cores_arestas_passo(grafo_nx, passo)
        colecao_arestas.set_color(cores_arestas)
        texto_info.set_text(_formatar_texto_passo(passo))
        estado_animacao["indice_atual"] = indice
        if titulo:
            eixo_grafo.set_title(f"{titulo} — etapa {indice + 1}/{len(passos)}")
        return colecao_vertices, colecao_arestas, texto_info

    def inicializar() -> Sequence[object]:
        if passos:
            cores_iniciais = _cores_vertices_passo(grafo_nx, passos[0])
            colecao_vertices.set_facecolor(cores_iniciais)
            cores_arestas_iniciais = _cores_arestas_passo(grafo_nx, passos[0])
            colecao_arestas.set_color(cores_arestas_iniciais)
            texto_info.set_text(_formatar_texto_passo(passos[0]))
        return colecao_vertices, colecao_arestas, texto_info

    animacao = FuncAnimation(
        fig,
        atualizar,
        frames=len(passos),
        interval=intervalo_base,
        repeat=False,
        init_func=inicializar,
        blit=False,
        cache_frame_data=False,
    )
    _registrar_animacao_ativa(fig, animacao)
    setattr(fig, "_animacao_ref", animacao)

    if mostrar:
        fig.subplots_adjust(top=0.9, bottom=0.18)

        area_botao = fig.add_axes([0.84, 0.88, 0.12, 0.08])
        area_botao.set_anchor("NE")
        area_botao.set_facecolor("#fee2e2")
        for spine in area_botao.spines.values():
            spine.set_visible(False)

        botao_fechar = Button(
            area_botao,
            label="✕ Fechar",
            color="#fee2e2",
            hovercolor="#fecaca",
        )
        botao_fechar.label.set_fontsize(12)
        botao_fechar.label.set_color("#7f1d1d")

        def _fechar_animacao(_event: object) -> None:
            _parar_animacao()
            plt.close(fig)

        botao_fechar.on_clicked(_fechar_animacao)

        total_passos = len(passos)
        texto_velocidade = fig.text(
            0.5,
            0.04,
            "Velocidade: 1.0×",
            ha="center",
            va="center",
            fontsize=10,
        )

        def _event_source() -> Any:
            return getattr(animacao, "event_source", None)

        def _parar_animacao() -> None:
            event_source = _event_source()
            if event_source is not None:
                event_source.stop()

        def _iniciar_animacao() -> None:
            event_source = _event_source()
            if event_source is not None:
                event_source.start()

        def _atualizar_intervalo_event_source(intervalo_ajustado: float) -> None:
            event_source = _event_source()
            if event_source is not None:
                event_source.interval = int(intervalo_ajustado)

        def _definir_intervalo(novo_intervalo: float) -> None:
            limite_inferior = 30.0
            limite_superior = 5000.0
            intervalo_ajustado = max(limite_inferior, min(limite_superior, novo_intervalo))
            estado_animacao["intervalo"] = intervalo_ajustado
            _atualizar_intervalo_event_source(intervalo_ajustado)
            fator = estado_animacao["intervalo_base"] / intervalo_ajustado
            texto_velocidade.set_text(f"Velocidade: {fator:.1f}×")
            fig.canvas.draw_idle()

        def _pausar_retomar(_event: object) -> None:
            if total_passos == 0:
                return
            pausado = bool(estado_animacao["pausado"])
            if pausado:
                _iniciar_animacao()
                botao_pausa.label.set_text("Pausar")
            else:
                _parar_animacao()
                botao_pausa.label.set_text("Despausar")
            estado_animacao["pausado"] = not pausado
            fig.canvas.draw_idle()

        def _mostrar_passo(indice: int) -> None:
            if total_passos == 0:
                return
            indice_limitado = max(0, min(total_passos - 1, indice))
            _parar_animacao()
            estado_animacao["pausado"] = True
            botao_pausa.label.set_text("Despausar")
            atualizar(indice_limitado)
            fig.canvas.draw_idle()
            proximo_indice = indice_limitado + 1 if indice_limitado < total_passos - 1 else indice_limitado
            animacao.frame_seq = iter(range(proximo_indice, total_passos))

        def _avancar(_event: object) -> None:
            indice_atual = int(estado_animacao["indice_atual"])
            _mostrar_passo(indice_atual + 1)

        def _voltar(_event: object) -> None:
            indice_atual = int(estado_animacao["indice_atual"])
            _mostrar_passo(indice_atual - 1)

        def _acelerar(_event: object) -> None:
            intervalo_atual = float(estado_animacao["intervalo"])
            _definir_intervalo(intervalo_atual * 0.5)

        def _desacelerar(_event: object) -> None:
            intervalo_atual = float(estado_animacao["intervalo"])
            _definir_intervalo(intervalo_atual * 2.0)

        largura_botao = 0.14
        altura_botao = 0.075
        espacamento = 0.025
        x_inicial = 0.14
        y_botao = 0.06

        painel_controles = fig.add_axes([0.08, 0.01, 0.84, 0.13])
        painel_controles.set_facecolor("#f1f5f9")
        painel_controles.set_xticks([])
        painel_controles.set_yticks([])
        for spine in painel_controles.spines.values():
            spine.set_visible(False)

        def _criar_eixo(indice_botao: int) -> "plt.Axes":
            eixo = fig.add_axes(
                [
                    x_inicial + indice_botao * (largura_botao + espacamento),
                    y_botao,
                    largura_botao,
                    altura_botao,
                ]
            )
            eixo.set_facecolor("#e2e8f0")
            for spine in eixo.spines.values():
                spine.set_visible(False)
            return eixo

        eixo_voltar = _criar_eixo(0)
        eixo_pausa = _criar_eixo(1)
        eixo_avancar = _criar_eixo(2)
        eixo_lento = _criar_eixo(3)
        eixo_rapido = _criar_eixo(4)

        botao_voltar = Button(
            eixo_voltar,
            label="Anterior",
            color="#e2e8f0",
            hovercolor="#cbd5f5",
        )
        botao_pausa = Button(
            eixo_pausa,
            label="Pausar",
            color="#e2e8f0",
            hovercolor="#cbd5f5",
        )
        botao_avancar = Button(
            eixo_avancar,
            label="Próximo",
            color="#e2e8f0",
            hovercolor="#cbd5f5",
        )
        botao_lento = Button(
            eixo_lento,
            label="- Veloc.",
            color="#e2e8f0",
            hovercolor="#cbd5f5",
        )
        botao_rapido = Button(
            eixo_rapido,
            label="+ Veloc.",
            color="#e2e8f0",
            hovercolor="#cbd5f5",
        )

        for button in (botao_voltar, botao_pausa, botao_avancar, botao_lento, botao_rapido):
            button.label.set_fontsize(11)
            button.label.set_color("#0f172a")

        botao_voltar.on_clicked(_voltar)
        botao_pausa.on_clicked(_pausar_retomar)
        botao_avancar.on_clicked(_avancar)
        botao_lento.on_clicked(_desacelerar)
        botao_rapido.on_clicked(_acelerar)

        estado_animacao["_controles"] = {
            "botao_fechar": botao_fechar,
            "botao_voltar": botao_voltar,
            "botao_pausa": botao_pausa,
            "botao_avancar": botao_avancar,
            "botao_lento": botao_lento,
            "botao_rapido": botao_rapido,
        }

        if total_passos == 0:
            botao_pausa.label.set_text("—")
            for button in (botao_voltar, botao_avancar, botao_lento, botao_rapido):
                button.label.set_color("#94a3b8")

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
        try:
            fig.canvas.manager.full_screen_toggle()  # type: ignore[union-attr]
        except AttributeError:
            pass
        plt.show()
    else:
        plt.close(fig)

    return animacao

