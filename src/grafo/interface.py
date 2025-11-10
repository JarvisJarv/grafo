"""Interface gráfica moderna para explorar grafos bipartidos."""
from __future__ import annotations

import sys
from io import StringIO
from pathlib import Path
from typing import Iterable, Optional

import networkx as nx
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
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
from .visualizacao import preparar_desenho


LAYOUT_OPCOES = {
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
        self._layout_atual: str = "spring"

        self._criar_componentes()
        self._carregar_exemplo_padrao()

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

        painel_controles = self._montar_painel_controles()
        splitter.addWidget(painel_controles)

        self.canvas = CanvasGrafo()
        painel_canvas = QWidget()
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
        layout = QVBoxLayout(painel)
        layout.setContentsMargins(12, 12, 12, 12)

        botao_abrir = QPushButton("Abrir arquivo .txt…")
        botao_abrir.clicked.connect(self._selecionar_arquivo)

        self.combo_exemplos = QComboBox()
        self.combo_exemplos.addItem("Escolher exemplo…", None)
        self.combo_exemplos.currentIndexChanged.connect(self._carregar_exemplo_combo)

        self.combo_layout = QComboBox()
        for descricao, valor in LAYOUT_OPCOES.items():
            self.combo_layout.addItem(descricao, userData=valor)
        self.combo_layout.currentIndexChanged.connect(self._alterar_layout)

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
        self.texto_relacionamentos.setStyleSheet("QTextEdit { background-color: #f3f4f6; }")
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
        layout.addWidget(botao_exportar)
        layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(painel)
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

        simbolos = {0: "🟦", 1: "🟧"}
        linhas = []
        for vertice in sorted(adjacencias.keys()):
            vizinhos = ", ".join(sorted(adjacencias[vertice])) or "nenhuma conexão"
            marcador = simbolos.get(cores.get(vertice, -1), "⬜")
            linhas.append(f"{marcador} <b>{vertice}</b> → {vizinhos}")
        self.texto_relacionamentos.setHtml("<br>".join(linhas))

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
        ax.set_facecolor("#f7f8fb")

        nx.draw_networkx_edges(grafo_nx, posicoes, ax=ax, edge_color=cores_arestas, width=2.4)
        nx.draw_networkx_nodes(
            grafo_nx,
            posicoes,
            ax=ax,
            node_color=cores_vertices,
            node_size=1100,
            linewidths=1.6,
            edgecolors="#2d2d2d",
        )
        nx.draw_networkx_labels(grafo_nx, posicoes, ax=ax, font_weight="bold")

        ax.set_axis_off()
        titulo = "Resultado do algoritmo"
        if self._arquivo_atual:
            titulo += f" — {self._arquivo_atual.name}"
        ax.set_title(titulo)

        legenda_itens = [
            ("🟦", "Partição 0"),
            ("🟧", "Partição 1"),
            ("🔴", "Conflito" if resultado.conflitos else "Conexão"),
        ]
        linhas = [f"{emoji} {texto}" for emoji, texto in legenda_itens]
        ax.text(
            0.02,
            0.02,
            "\n".join(linhas),
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=10,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.9),
        )

        self.canvas.draw_idle()

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
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
              dois vértices por linha representando uma relação.</li>
          <li>O algoritmo aceita qualquer grafo bipartido, mas nos exemplos usamos
              usuários conectando-se a filmes que assistiram.</li>
        </ul>
        <p>Exemplo mínimo:</p>
        <pre># usuários à esquerda, filmes à direita
gabriel filme_matrix
gabriel filme_mad_max
larissa filme_meu_vizinho_totoro</pre>
        """

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
