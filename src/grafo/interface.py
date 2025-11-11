"""Interface gráfica moderna para explorar grafos bipartidos."""
from __future__ import annotations

import sys
from collections import Counter
from io import StringIO
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Dict, Iterable, List, Optional, Sequence, Tuple

import networkx as nx
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Ellipse, FancyArrowPatch
from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .bipartido import GrafoBipartido, ResultadoBiparticao
from .io import carregar_de_iteravel
from .visualizacao import _deslocar_rotulos, animar_verificacao, preparar_desenho


CORES_PARTICOES = {
    0: ("#1d4ed8", "#bfdbfe"),
    1: ("#c2410c", "#fed7aa"),
}

if TYPE_CHECKING:  # pragma: no cover - apenas para dicas de tipo
    from matplotlib.axes import Axes


LAYOUT_OPCOES = {
    "Diagrama bipartido (flechas)": "flechas",
    "Layout automático (spring)": "spring",
    "Círculo": "circular",
    "Kamada-Kawai": "kamada_kawai",
    "Colunas bipartidas": "bipartido",
}


def _carregar_template() -> str:
    return "\n".join(
        [
            "# Exemplo de grafo bipartido para recomendações",
            "[vertices]",
            "usuario_gabriel tipo=usuario",
            "usuario_marcelo tipo=usuario",
            "usuario_larissa tipo=usuario",
            "filme_matrix tipo=filme",
            "filme_mad_max tipo=filme",
            "filme_meu_vizinho_totoro tipo=filme",
            "[arestas]",
            "usuario_gabriel filme_matrix",
            "usuario_gabriel filme_mad_max",
            "usuario_marcelo filme_mad_max",
            "usuario_larissa filme_meu_vizinho_totoro",
        ]
    )


class CanvasGrafo(FigureCanvas):
    """Canvas do Matplotlib configurado para ocupar todo o espaço disponível."""

    def __init__(self) -> None:
        self.figure = Figure(figsize=(6, 5), tight_layout=True)
        super().__init__(self.figure)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()


class VisualizadorBipartido(QMainWindow):
    """Janela principal para visualização dos grafos."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Explorador de Grafos Bipartidos — Recomendações de Filmes")
        self.setMinimumSize(1200, 760)

        self._grafo = GrafoBipartido()
        self._resultado: Optional[ResultadoBiparticao] = None
        self._arquivo_atual: Optional[Path] = None
        self._layout_atual: str = "flechas"

        self._aplicar_tema_moderno()
        self._criar_componentes()
        self._carregar_exemplo_padrao()
        self.setWindowState(self.windowState() | Qt.WindowMaximized)

    # ------------------------------------------------------------------
    # Construção da interface
    # ------------------------------------------------------------------
    def _criar_componentes(self) -> None:
        abas = QTabWidget()
        abas.addTab(self._criar_aba_visualizacao(), "Visualizar grafo")
        abas.addTab(self._criar_aba_editor(), "Criar arquivo .txt")
        self.setCentralWidget(abas)

    def _criar_aba_visualizacao(self) -> QWidget:
        conteudo = QWidget()
        layout = QHBoxLayout(conteudo)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(6)

        painel_controles = self._montar_painel_controles()
        splitter.addWidget(painel_controles)

        self.canvas = CanvasGrafo()
        painel_canvas = QWidget()
        painel_canvas.setObjectName("PainelCanvas")
        layout_canvas = QVBoxLayout(painel_canvas)
        layout_canvas.setContentsMargins(12, 12, 12, 12)
        layout_canvas.addWidget(self.canvas)
        splitter.addWidget(painel_canvas)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)
        return conteudo

    def _montar_painel_controles(self) -> QWidget:
        painel = QWidget()
        painel.setObjectName("PainelControles")
        painel.setMinimumWidth(380)
        layout = QVBoxLayout(painel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)

        botao_abrir = QPushButton("Abrir arquivo .txt…")
        botao_abrir.clicked.connect(self._selecionar_arquivo)

        self.combo_exemplos = QComboBox()
        self.combo_exemplos.addItem("Escolher exemplo…", None)
        self.combo_exemplos.currentIndexChanged.connect(self._carregar_exemplo_combo)

        self.combo_layout = QComboBox()
        for descricao, valor in LAYOUT_OPCOES.items():
            self.combo_layout.addItem(descricao, userData=valor)
        self.combo_layout.currentIndexChanged.connect(self._alterar_layout)
        indice_layout_padrao = self.combo_layout.findData(self._layout_atual)
        if indice_layout_padrao >= 0:
            self.combo_layout.setCurrentIndex(indice_layout_padrao)

        botoes_layout = QWidget()
        botoes_layout_linha = QHBoxLayout(botoes_layout)
        botoes_layout_linha.setContentsMargins(0, 0, 0, 0)
        botoes_layout_linha.addWidget(QLabel("Layout:"))
        botoes_layout_linha.addWidget(self.combo_layout)

        self.rotulo_arquivo = QLabel("Nenhum arquivo carregado")
        self.rotulo_arquivo.setWordWrap(True)

        grupo_resumo = QGroupBox("Resumo do algoritmo")
        layout_resumo = QFormLayout(grupo_resumo)
        self.rotulo_status = QLabel("Carregue um grafo para iniciar")
        self.rotulo_particao_a = QLabel("—")
        self.rotulo_particao_b = QLabel("—")
        self.rotulo_conflitos = QLabel("—")
        layout_resumo.addRow("Situação:", self.rotulo_status)
        layout_resumo.addRow("Partição 0:", self.rotulo_particao_a)
        layout_resumo.addRow("Partição 1:", self.rotulo_particao_b)
        layout_resumo.addRow("Conflitos:", self.rotulo_conflitos)

        grupo_relacionamentos = QGroupBox("Relacionamentos detectados")
        layout_rel = QVBoxLayout(grupo_relacionamentos)
        self.texto_relacionamentos = QTextEdit()
        self.texto_relacionamentos.setReadOnly(True)
        self.texto_relacionamentos.setMinimumHeight(240)
        self.texto_relacionamentos.setMinimumWidth(0)
        self.texto_relacionamentos.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.texto_relacionamentos.setStyleSheet(
            "QTextEdit {"
            " background-color: #0f172a;"
            " color: #e2e8f0;"
            " border-radius: 10px;"
            " border: 1px solid rgba(148, 163, 184, 0.35);"
            " padding: 12px;"
            " font-family: 'JetBrains Mono', 'Fira Code', monospace;"
            " font-size: 13px;"
            " line-height: 1.55;"
            " }\n"
            " QTextEdit QScrollBar:vertical {width: 10px;}"
        )
        layout_rel.addWidget(self.texto_relacionamentos)

        grupo_ajuda = QGroupBox("Formato do arquivo .txt")
        layout_ajuda = QVBoxLayout(grupo_ajuda)
        self.texto_ajuda = QTextEdit()
        self.texto_ajuda.setReadOnly(True)
        self.texto_ajuda.setHtml(self._gerar_texto_ajuda())
        layout_ajuda.addWidget(self.texto_ajuda)

        botao_exportar = QPushButton("Exportar visualização…")
        botao_exportar.clicked.connect(self._exportar_imagem)

        layout.addWidget(botao_abrir)
        layout.addWidget(self.combo_exemplos)
        layout.addWidget(botoes_layout)
        layout.addWidget(self.rotulo_arquivo)
        layout.addWidget(grupo_resumo)
        layout.addWidget(grupo_relacionamentos)
        layout.addWidget(grupo_ajuda)
        botao_animacao = QPushButton("Ver animação do algoritmo")
        botao_animacao.clicked.connect(self._mostrar_animacao)

        layout.addWidget(botao_exportar)
        layout.addWidget(botao_animacao)
        layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(painel)
        scroll.setObjectName("ScrollPainel")
        return scroll

    def _criar_aba_editor(self) -> QWidget:
        conteudo = QWidget()
        layout = QVBoxLayout(conteudo)
        layout.setContentsMargins(12, 12, 12, 12)

        descricao = QLabel(
            "Escreva ou cole o conteúdo do grafo bipartido. Você pode salvar em um arquivo "
            "ou enviar diretamente para a aba de visualização."
        )
        descricao.setWordWrap(True)

        self.editor_texto = QPlainTextEdit()
        self.editor_texto.setPlainText(_carregar_template())
        self.editor_texto.setMinimumHeight(320)

        botoes = QWidget()
        layout_botoes = QHBoxLayout(botoes)
        layout_botoes.setContentsMargins(0, 0, 0, 0)

        botao_salvar = QPushButton("Salvar como…")
        botao_salvar.clicked.connect(self._salvar_texto_como)

        botao_usar = QPushButton("Visualizar este texto")
        botao_usar.clicked.connect(self._usar_texto_editor)

        layout_botoes.addWidget(botao_salvar)
        layout_botoes.addWidget(botao_usar)
        layout_botoes.addStretch(1)

        layout.addWidget(descricao)
        layout.addWidget(self.editor_texto)
        layout.addWidget(botoes)
        layout.addStretch(1)

        return conteudo

    # ------------------------------------------------------------------
    # Operações
    # ------------------------------------------------------------------
    def _selecionar_arquivo(self) -> None:
        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar arquivo de grafo",
            str(self._pasta_base()),
            "Arquivos de texto (*.txt);;Todos os arquivos (*)",
        )
        if arquivo:
            self._carregar_arquivo(Path(arquivo))

    def _carregar_arquivo(self, caminho: Path) -> None:
        try:
            self._grafo.carregar_de_arquivo(str(caminho))
            self._resultado = self._grafo.verificar_biparticao()
            self._arquivo_atual = caminho
            self.rotulo_arquivo.setText(f"Arquivo carregado: <b>{caminho.name}</b>")
            self.statusBar().showMessage(f"Arquivo carregado: {caminho}")
            self._atualizar_interface()
        except Exception as exc:  # pragma: no cover - interface
            self._mostrar_erro("Não foi possível carregar o arquivo", exc)

    def _carregar_exemplo_padrao(self) -> None:
        pasta_exemplos = self._pasta_base() / "exemplos"
        if not pasta_exemplos.exists():
            return

        for caminho in sorted(pasta_exemplos.glob("*.txt")):
            self.combo_exemplos.addItem(caminho.name, userData=caminho)

        preferidos = [
            "recomendacao_sucesso.txt",
            "recomendacao_conflito.txt",
            "usuario_filme_equilibrado.txt",
            "usuario_filme_tendencias.txt",
            "bipartido.txt",
        ]
        for nome in preferidos:
            arquivo = pasta_exemplos / nome
            if arquivo.exists():
                self._carregar_arquivo(arquivo)
                indice = self.combo_exemplos.findData(arquivo)
                if indice >= 0:
                    self.combo_exemplos.setCurrentIndex(indice)
                break

    def _carregar_exemplo_combo(self, indice: int) -> None:
        caminho = self.combo_exemplos.itemData(indice)
        if isinstance(caminho, Path):
            self._carregar_arquivo(caminho)

    def _alterar_layout(self, indice: int) -> None:
        layout = self.combo_layout.itemData(indice)
        if layout:
            self._layout_atual = str(layout)
            self._desenhar_grafo()

    def _salvar_texto_como(self) -> None:
        texto = self.editor_texto.toPlainText().strip()
        if not texto:
            QMessageBox.warning(self, "Conteúdo vazio", "Preencha o texto do grafo antes de salvar.")
            return

        caminho, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar arquivo de grafo",
            str(self._pasta_base() / "meu_grafo.txt"),
            "Arquivos de texto (*.txt)",
        )
        if caminho:
            try:
                Path(caminho).write_text(texto + "\n", encoding="utf-8")
                self.statusBar().showMessage(f"Arquivo salvo em {caminho}")
            except Exception as exc:  # pragma: no cover - interface
                self._mostrar_erro("Não foi possível salvar o arquivo", exc)

    def _usar_texto_editor(self) -> None:
        texto = self.editor_texto.toPlainText().strip()
        if not texto:
            QMessageBox.warning(self, "Conteúdo vazio", "Escreva um grafo antes de visualizar.")
            return

        linhas: Iterable[str] = StringIO(texto).read().splitlines()
        try:
            dados = carregar_de_iteravel(linhas)
            self._grafo.carregar(dados)
            self._resultado = self._grafo.verificar_biparticao()
            self._arquivo_atual = None
            self.rotulo_arquivo.setText("Visualizando grafo a partir do editor")
            self.statusBar().showMessage("Grafo carregado a partir do editor de texto")
            self._atualizar_interface()
        except Exception as exc:  # pragma: no cover - interface
            self._mostrar_erro("Erro ao interpretar o texto informado", exc)

    def _exportar_imagem(self) -> None:
        if self._resultado is None:
            QMessageBox.information(self, "Nada para exportar", "Carregue um grafo antes de exportar.")
            return

        caminho, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar visualização",
            str(self._pasta_base() / "grafo.png"),
            "PNG (*.png);;SVG (*.svg)",
        )
        if caminho:
            try:
                self.canvas.figure.savefig(caminho, dpi=150)
                self.statusBar().showMessage(f"Visualização salva em {caminho}")
            except Exception as exc:  # pragma: no cover - interface
                self._mostrar_erro("Não foi possível exportar a figura", exc)

    def _mostrar_animacao(self) -> None:
        if self._resultado is None:
            QMessageBox.information(self, "Nada para animar", "Carregue um grafo antes de assistir à animação.")
            return

        layout_animacao = "bipartido" if self._layout_atual == "flechas" else self._layout_atual
        titulo = "Execução passo a passo do algoritmo"
        if self._arquivo_atual:
            titulo += f" — {self._arquivo_atual.name}"

        try:
            animar_verificacao(
                self._grafo,
                layout=layout_animacao,
                titulo=titulo,
                mostrar=True,
            )
        except RuntimeError as exc:  # pragma: no cover - interface
            self._mostrar_erro("Não foi possível exibir a animação", exc)
        except Exception as exc:  # pragma: no cover - interface
            self._mostrar_erro("Falha inesperada ao abrir a animação", exc)

    # ------------------------------------------------------------------
    # Atualização de conteúdo
    # ------------------------------------------------------------------
    def _atualizar_interface(self) -> None:
        if not self._resultado:
            return

        self._atualizar_resumo()
        self._atualizar_relacionamentos()
        self._desenhar_grafo()

    def _atualizar_resumo(self) -> None:
        assert self._resultado is not None

        if self._resultado.eh_bipartido:
            self.rotulo_status.setText("✅ Grafo bipartido — nenhuma aresta conflitante")
        else:
            total = len(self._resultado.conflitos)
            self.rotulo_status.setText(
                f"⚠️ Conflitos detectados — {total} aresta{'s' if total > 1 else ''} fora da bipartição"
            )

        particao_a, particao_b = self._resultado.particoes
        self.rotulo_particao_a.setText(
            f"{len(particao_a)} vértice{'s' if len(particao_a) != 1 else ''}: {', '.join(sorted(particao_a)) or '∅'}"
        )
        self.rotulo_particao_b.setText(
            f"{len(particao_b)} vértice{'s' if len(particao_b) != 1 else ''}: {', '.join(sorted(particao_b)) or '∅'}"
        )

        if self._resultado.conflitos:
            conflitos = "<br>".join(" — ".join(aresta) for aresta in self._resultado.conflitos)
            self.rotulo_conflitos.setText(conflitos)
        else:
            self.rotulo_conflitos.setText("Nenhum")

    def _atualizar_relacionamentos(self) -> None:
        assert self._resultado is not None
        adjacencias = self._grafo.adjacencias()
        cores = self._resultado.cores
        atributos = self._grafo.atributos()
        tipos_particoes = self._grafo.tipos_por_particao()
        conflitos = {tuple(sorted(aresta)) for aresta in self._resultado.conflitos}

        if not adjacencias:
            html_vazio = (
                "<html><head>"
                f"{self._estilos_relacionamentos()}"
                "</head><body><div class='painel vazio'>"
                "<p class='mensagem-vazia'>Nenhum relacionamento disponível.</p>"
                "</div></body></html>"
            )
            self.texto_relacionamentos.setHtml(html_vazio)
            return

        grupos: Dict[str, Dict[str, object]] = {}
        for vertice in sorted(adjacencias.keys()):
            cor_vertice = cores.get(vertice, -1)
            dados_vertice = atributos.get(vertice, {})
            tipo = dados_vertice.get("tipo") or tipos_particoes.get(cor_vertice)
            if tipo:
                etiqueta = tipo.replace("_", " ").title()
            elif cor_vertice in (0, 1):
                etiqueta = f"Partição {cor_vertice}"
            else:
                etiqueta = "Sem partição"

            chave_grupo = str(cor_vertice) if cor_vertice in (0, 1) else "sem"
            info = grupos.setdefault(
                chave_grupo,
                {
                    "cor": cor_vertice if cor_vertice in (0, 1) else -1,
                    "linhas": [],
                    "tipos": Counter(),
                    "total_relacoes": 0,
                },
            )

            if tipo:
                info["tipos"][tipo] += 1

            destinos: List[str] = []
            for vizinho in sorted(adjacencias[vertice]):
                aresta = tuple(sorted((vertice, vizinho)))
                classe = "destino conflito" if aresta in conflitos else "destino vizinho"
                destinos.append(f"<li class='{classe}'>{vizinho}</li>")

            if destinos:
                destinos_html = "<ul class='lista-destinos'>" + "".join(destinos) + "</ul>"
                contador = f"{len(destinos)} relação{'es' if len(destinos) != 1 else ''}"
            else:
                destinos_html = "<div class='lista-destinos vazio'>Sem conexões registradas</div>"
                contador = "Nenhuma relação"

            info["total_relacoes"] += len(destinos)

            linha = (
                "<tr>"
                f"<th scope='row' class='col-origem'>{vertice}</th>"
                f"<td class='col-tipo'>{etiqueta}</td>"
                f"<td class='col-relacoes'>{destinos_html}<span class='contador'>{contador}</span></td>"
                "</tr>"
            )
            info.setdefault("linhas", []).append(linha)

        secoes: List[str] = []
        total_vertices = len(adjacencias)
        total_relacoes = sum(len(v) for v in adjacencias.values())
        total_conflitos = len(conflitos)

        resumo_html = (
            "<section class='resumo'>"
            f"<div class='resumo-item'><span class='resumo-numero'>{total_vertices}</span>"
            "<span class='resumo-legenda'>vértice(s) listados</span></div>"
            f"<div class='resumo-item'><span class='resumo-numero'>{total_relacoes}</span>"
            "<span class='resumo-legenda'>relações mapeadas</span></div>"
            f"<div class='resumo-item destaque'><span class='resumo-numero'>{total_conflitos}</span>"
            "<span class='resumo-legenda'>arestas em conflito</span></div>"
            "</section>"
        )
        secoes.append(resumo_html)

        for chave in ("0", "1", "sem"):
            info = grupos.get(chave)
            if not info:
                continue

            cor_grupo = int(info["cor"]) if isinstance(info["cor"], int) else -1
            linhas = info.get("linhas", [])
            total_rel = int(info.get("total_relacoes", 0))
            total_vertices_grupo = len(linhas)

            if cor_grupo in (0, 1):
                titulo = f"Partição {cor_grupo}"
                rotulo_base = tipos_particoes.get(cor_grupo)
                if not rotulo_base and isinstance(info["tipos"], Counter) and info["tipos"]:
                    rotulo_base = info["tipos"].most_common(1)[0][0]
                descricao = (
                    rotulo_base.replace("_", " ").title()
                    if rotulo_base
                    else "Sem rótulo definido"
                )
                classe_grupo = f"grupo grupo-{cor_grupo}"
            else:
                titulo = "Sem partição definida"
                if isinstance(info["tipos"], Counter) and info["tipos"]:
                    descricoes = {
                        chave_tipo.replace("_", " ").title()
                        for chave_tipo in info["tipos"].keys()
                    }
                    descricao = ", ".join(sorted(descricoes))
                else:
                    descricao = "Vértices não classificados"
                classe_grupo = "grupo grupo-outros"

            resumo = (
                f"{total_vertices_grupo} vértice{'s' if total_vertices_grupo != 1 else ''}"
                " • "
                + (
                    f"{total_rel} relação{'es' if total_rel != 1 else ''}"
                    if total_rel
                    else "nenhuma relação"
                )
            )

            tabela = (
                "<table class='tabela-relacoes'>"
                "<thead><tr>"
                "<th class='col-origem'>Origem</th>"
                "<th class='col-tipo'>Categoria</th>"
                "<th class='col-relacoes'>Destinos</th>"
                "</tr></thead>"
                "<tbody>"
                + "".join(linhas)
                + "</tbody></table>"
            )

            grupo_html = (
                f"<section class='{classe_grupo}'>"
                "<header class='grupo-cabecalho'>"
                "<div class='grupo-info'>"
                f"<span class='grupo-etiqueta'>{titulo}</span>"
                f"<span class='grupo-descricao'>{descricao}</span>"
                "</div>"
                f"<span class='grupo-resumo'>{resumo}</span>"
                "</header>"
                + tabela
                + "</section>"
            )
            secoes.append(grupo_html)

        html = (
            "<html><head>"
            f"{self._estilos_relacionamentos()}"
            "</head><body><div class='painel'>"
            + "".join(secoes)
            + "</div></body></html>"
        )
        self.texto_relacionamentos.setHtml(html)

    def _desenhar_grafo(self) -> None:
        if self._resultado is None:
            self.canvas.figure.clear()
            ax = self.canvas.figure.add_subplot(111)
            ax.text(0.5, 0.5, "Carregue um grafo para visualizar", ha="center", va="center")
            ax.axis("off")
            self.canvas.draw_idle()
            return

        grafo_nx, posicoes, cores_vertices, cores_arestas, resultado = preparar_desenho(
            self._grafo, layout=self._layout_atual
        )

        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)
        if self._layout_atual == "flechas":
            ax.set_facecolor("#f8fafc")
            self._desenhar_regioes_particao(ax, posicoes, resultado)
            orientacoes = {
                tuple(sorted(aresta)): aresta for aresta in self._grafo.arestas
            }
            colecao_arestas = self._desenhar_arestas_flechas(
                ax, grafo_nx, posicoes, cores_arestas, orientacoes
            )
        else:
            ax.set_facecolor("#f7f8fb")
            colecao_arestas = nx.draw_networkx_edges(
                grafo_nx,
                posicoes,
                ax=ax,
                edge_color=cores_arestas,
                width=2.4,
            )
        colecao_vertices = nx.draw_networkx_nodes(
            grafo_nx,
            posicoes,
            ax=ax,
            node_color=cores_vertices,
            node_size=1100,
            linewidths=1.6,
            edgecolors="#2d2d2d",
        )
        posicoes_rotulos = _deslocar_rotulos(posicoes)
        rotulos = nx.draw_networkx_labels(
            grafo_nx,
            posicoes_rotulos,
            ax=ax,
            font_weight="bold",
            verticalalignment="bottom",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="none", alpha=0.85),
        )

        # Ajusta a ordem de desenho para manter os elementos visuais na hierarquia correta
        if isinstance(colecao_arestas, list):
            for artista in colecao_arestas:
                artista.set_zorder(1)
        elif colecao_arestas is not None:
            colecao_arestas.set_zorder(1)
        if colecao_vertices is not None:
            colecao_vertices.set_zorder(2)
        for texto in rotulos.values():
            texto.set_zorder(3)

        ax.set_axis_off()
        titulo = "Resultado do algoritmo"
        if self._arquivo_atual:
            titulo += f" — {self._arquivo_atual.name}"
        ax.set_title(titulo)

        self.canvas.draw_idle()

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def _aplicar_tema_moderno(self) -> None:
        estilo = dedent(
            """
            QMainWindow {
                background-color: #0f172a;
            }
            QWidget {
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 13px;
                color: #e2e8f0;
            }
            QSplitter::handle {
                background-color: rgba(148, 163, 184, 0.35);
                margin: 0 6px;
            }
            QWidget#PainelCanvas {
                background-color: #111c33;
                border-radius: 16px;
            }
            QWidget#PainelControles {
                background-color: rgba(15, 23, 42, 0.92);
                border-radius: 18px;
                border: 1px solid rgba(148, 163, 184, 0.25);
            }
            QScrollArea#ScrollPainel {
                border: none;
                background-color: transparent;
            }
            QScrollArea#ScrollPainel > QWidget > QWidget {
                background: transparent;
            }
            QGroupBox {
                border: 1px solid rgba(148, 163, 184, 0.35);
                border-radius: 12px;
                margin-top: 12px;
                padding: 10px 14px 14px 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 6px;
                color: #f8fafc;
                font-weight: 600;
            }
            QLabel {
                line-height: 1.4;
            }
            QPushButton {
                background-color: #2563eb;
                border: none;
                border-radius: 10px;
                padding: 10px 16px;
                color: white;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e3a8a;
            }
            QPushButton:disabled {
                background-color: rgba(37, 99, 235, 0.35);
                color: rgba(255, 255, 255, 0.55);
            }
            QComboBox {
                padding: 8px 12px;
                border-radius: 10px;
                background-color: rgba(30, 41, 59, 0.92);
                border: 1px solid rgba(148, 163, 184, 0.35);
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #1f2937;
                border-radius: 8px;
                selection-background-color: #2563eb;
                selection-color: white;
            }
            QPlainTextEdit, QTextEdit {
                background-color: rgba(15, 23, 42, 0.85);
                border-radius: 12px;
                border: 1px solid rgba(148, 163, 184, 0.35);
                padding: 12px;
            }
            QPlainTextEdit {
                font-family: 'JetBrains Mono', 'Fira Code', monospace;
            }
            QStatusBar {
                background-color: rgba(15, 23, 42, 0.9);
                border-top: 1px solid rgba(148, 163, 184, 0.35);
            }
            """
        )
        self.setStyleSheet(estilo)
        self.statusBar().setStyleSheet("color: #e2e8f0;")

    def _desenhar_arestas_flechas(
        self,
        ax: "Axes",
        grafo_nx: nx.Graph,
        posicoes: Dict[str, Sequence[float]],
        cores_arestas: Sequence[str],
        orientacoes: Dict[Tuple[str, str], Tuple[str, str]] | None = None,
    ) -> List[FancyArrowPatch]:
        flechas: List[FancyArrowPatch] = []
        arestas = list(grafo_nx.edges)
        for (origem, destino), cor in zip(arestas, cores_arestas):
            chave = tuple(sorted((origem, destino)))
            origem_real, destino_real = (
                orientacoes.get(chave, (origem, destino)) if orientacoes else (origem, destino)
            )

            if origem_real not in posicoes or destino_real not in posicoes:
                continue

            inicio = posicoes[origem_real]
            fim = posicoes[destino_real]
            if inicio == fim:
                continue

            flecha = FancyArrowPatch(
                inicio,
                fim,
                arrowstyle="-|>",
                mutation_scale=26,
                linewidth=2.6,
                color=cor,
                alpha=0.95,
                connectionstyle="arc3,rad=0.0",
                shrinkA=18,
                shrinkB=18,
            )
            flecha.set_zorder(1)
            ax.add_patch(flecha)
            flechas.append(flecha)

        return flechas

    def _desenhar_regioes_particao(
        self,
        ax: "Axes",
        posicoes: Dict[str, Sequence[float]],
        resultado: ResultadoBiparticao,
    ) -> None:
        tipos_particoes = self._grafo.tipos_por_particao()

        for indice, vertices in enumerate(resultado.particoes):
            pontos = [posicoes[vertice] for vertice in vertices if vertice in posicoes]
            if not pontos:
                continue

            xs = [ponto[0] for ponto in pontos]
            ys = [ponto[1] for ponto in pontos]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            padding_x = max(0.12, (max_x - min_x) * 0.45)
            padding_y = max(0.12, (max_y - min_y) * 0.55)

            centro_x = (min_x + max_x) / 2
            centro_y = (min_y + max_y) / 2
            largura = (max_x - min_x) + 2 * padding_x
            altura = (max_y - min_y) + 2 * padding_y

            cor_borda, cor_preenchimento = CORES_PARTICOES.get(indice, ("#334155", "#cbd5f5"))
            ellipse = Ellipse(
                (centro_x, centro_y),
                width=largura,
                height=altura,
                facecolor=cor_preenchimento,
                edgecolor=cor_borda,
                linewidth=2.4,
                alpha=0.22,
                zorder=0,
            )
            ax.add_patch(ellipse)

            rotulo = tipos_particoes.get(indice)
            if rotulo:
                texto = rotulo.replace("_", " ").title()
            else:
                texto = f"Partição {indice}"

            ax.text(
                centro_x,
                centro_y + altura / 2.15,
                texto,
                ha="center",
                va="bottom",
                color=cor_borda,
                fontsize=12,
                fontweight="bold",
                alpha=0.85,
                zorder=1,
            )

    def _mostrar_erro(self, titulo: str, erro: Exception) -> None:
        QMessageBox.critical(self, titulo, f"{titulo}:\n{erro}")

    @staticmethod
    def _pasta_base() -> Path:
        return Path(__file__).resolve().parents[2]

    def _gerar_texto_ajuda(self) -> str:
        return """
        <h3>Como montar o arquivo</h3>
        <ul>
          <li>Use <code>#</code> para comentários.</li>
          <li>A seção <code>[vertices]</code> é opcional e permite definir atributos.
              Utilize <code>pos=x,y</code> ou <code>x=</code>/<code>y=</code> para posicionar.</li>
          <li>Na seção <code>[arestas]</code> (ou fora de qualquer seção) liste
              dois vértices por linha representando uma relação. Você pode usar
              tanto <code>origem destino</code> quanto <code>origem x destino</code>
              para destacar a ligação.</li>
          <li>O algoritmo aceita qualquer grafo bipartido, mas nos exemplos usamos
              usuários conectando-se a filmes que assistiram.</li>
        </ul>
        <p>Exemplo mínimo:</p>
        <pre># usuários à esquerda, filmes à direita
gabriel x filme_matrix
gabriel x filme_mad_max
larissa x filme_meu_vizinho_totoro</pre>
        """

    @staticmethod
    def _estilos_relacionamentos() -> str:
        estilos = dedent(
            """
            <style>
            body {margin: 0; background-color: transparent; color: #e2e8f0; font-family: 'Inter', 'Segoe UI', sans-serif;}
            .painel {display: flex; flex-direction: column; gap: 16px; padding: 8px 0 16px;}
            .painel.vazio {min-height: 160px; align-items: center; justify-content: center; display: flex;}
            .mensagem-vazia {margin: 0; padding: 20px; border-radius: 14px; background: rgba(15, 23, 42, 0.72);
                             border: 1px solid rgba(148, 163, 184, 0.28); font-weight: 600; letter-spacing: 0.01em;}
            .resumo {display: flex; flex-wrap: wrap; gap: 12px; background: rgba(15, 23, 42, 0.7);
                     border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 16px; padding: 14px 16px;}
            .resumo-item {display: flex; flex-direction: column; gap: 2px; padding: 10px 12px; border-radius: 12px;
                          background: rgba(30, 41, 59, 0.58); min-width: 120px;}
            .resumo-item.destaque {background: rgba(248, 113, 113, 0.14); border: 1px solid rgba(248, 113, 113, 0.32);}
            .resumo-numero {font-size: 22px; font-weight: 700; color: #f8fafc; line-height: 1.1;}
            .resumo-item.destaque .resumo-numero {color: #fca5a5;}
            .resumo-legenda {font-size: 12px; font-weight: 600; color: #cbd5f5; text-transform: uppercase; letter-spacing: 0.08em;}
            .grupo {display: flex; flex-direction: column; gap: 0; border-radius: 18px; overflow: hidden;
                    border: 1px solid rgba(148, 163, 184, 0.18); background: rgba(15, 23, 42, 0.64);}
            .grupo-0 {border-color: rgba(59, 130, 246, 0.32);}
            .grupo-1 {border-color: rgba(234, 88, 12, 0.32);}
            .grupo-cabecalho {display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-start;
                              gap: 10px; padding: 16px 18px; background: rgba(15, 23, 42, 0.78);}
            .grupo-info {display: flex; flex-direction: column; gap: 6px; min-width: 0;}
            .grupo-etiqueta {font-size: 12px; text-transform: uppercase; letter-spacing: 0.12em; font-weight: 700; color: #38bdf8;}
            .grupo.grupo-1 .grupo-etiqueta {color: #fb923c;}
            .grupo.grupo-outros .grupo-etiqueta {color: #cbd5f5;}
            .grupo-descricao {font-size: 18px; font-weight: 600; color: #f8fafc; word-break: break-word;}
            .grupo-resumo {font-size: 13px; font-weight: 600; color: #cbd5f5; background: rgba(15, 23, 42, 0.55);
                          border-radius: 999px; padding: 6px 14px; border: 1px solid rgba(148, 163, 184, 0.28);}
            .tabela-relacoes {width: 100%; border-collapse: collapse; background: rgba(15, 23, 42, 0.82);}
            .tabela-relacoes thead {background: rgba(30, 41, 59, 0.8);}
            .tabela-relacoes th {font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; color: #a5b4fc;}
            .tabela-relacoes th, .tabela-relacoes td {padding: 14px 18px; border-bottom: 1px solid rgba(148, 163, 184, 0.16); vertical-align: top;}
            .tabela-relacoes tbody tr:last-child th, .tabela-relacoes tbody tr:last-child td {border-bottom: none;}
            .col-origem {width: 26%; font-weight: 700; color: #f8fafc; word-break: break-word;}
            .col-tipo {width: 20%; color: #e2e8f0; font-weight: 500;}
            .col-relacoes {width: 54%;}
            .lista-destinos {display: flex; flex-wrap: wrap; gap: 6px; list-style: none; margin: 0; padding: 0;}
            .lista-destinos.vazio {display: inline-flex; align-items: center; padding: 6px 10px; border-radius: 999px;
                                   border: 1px dashed rgba(148, 163, 184, 0.4); color: #cbd5f5; font-style: italic;}
            .destino {display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 999px; font-size: 12px;
                      background: rgba(14, 116, 233, 0.15); border: 1px solid rgba(56, 189, 248, 0.28); color: #bae6fd;}
            .destino::before {content: '•'; font-size: 14px; color: rgba(56, 189, 248, 0.9);}
            .destino.conflito {background: rgba(248, 113, 113, 0.2); border-color: rgba(248, 113, 113, 0.36); color: #fecaca; font-weight: 600;}
            .destino.conflito::before {content: '⚠'; color: #f87171;}
            .contador {display: block; margin-top: 6px; font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.06em;}
            @media (max-width: 720px) {
              .resumo {flex-direction: column;}
              .resumo-item {width: 100%;}
              .grupo-cabecalho {padding: 14px;}
              .tabela-relacoes th, .tabela-relacoes td {padding: 12px 14px;}
            }
            </style>
            """
        )
        return estilos.strip()
    # ------------------------------------------------------------------
    # Eventos
    # ------------------------------------------------------------------
    def closeEvent(self, event: QCloseEvent) -> None:  # pragma: no cover - evento da interface
        self.statusBar().showMessage("Até logo!")
        super().closeEvent(event)


def main() -> None:
    """Ponto de entrada para a aplicação PySide6."""

    app = QApplication.instance() or QApplication(sys.argv)
    janela = VisualizadorBipartido()
    janela.show()
    sys.exit(app.exec())


if __name__ == "__main__":  # pragma: no cover - execução direta
    main()
