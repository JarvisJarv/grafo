"""Gera capturas e animações da visualização do grafo bipartido."""
from __future__ import annotations

from pathlib import Path
import sys

# Garante que ``import grafo`` funcione mesmo sem instalar o pacote.
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR / "src"))

import matplotlib

# Backend "Agg" evita a necessidade de um display durante a geração das figuras.
matplotlib.use("Agg")

from grafo.bipartido import GrafoBipartido
from grafo.visualizacao import animar_verificacao, exibir_grafo


def _carregar_grafo(caminho: Path) -> GrafoBipartido:
    grafo = GrafoBipartido()
    grafo.carregar_de_arquivo(str(caminho))
    grafo.verificar_biparticao()
    return grafo


def gerar_captura_estatica(caminho_grafo: Path, destino: Path, *, layout: str = "spring") -> None:
    """Gera uma imagem estática do grafo com a coloração final."""

    grafo = _carregar_grafo(caminho_grafo)
    exibir_grafo(
        grafo,
        layout=layout,
        titulo="Coloração final: grafo bipartido",
        mostrar=False,
        caminho_saida=destino,
    )


def gerar_animacao_coloracao(
    caminho_grafo: Path,
    destino: Path,
    *,
    layout: str = "spring",
    intervalo_ms: int = 1200,
) -> None:
    """Gera uma animação GIF mostrando o processo de coloração passo a passo."""

    grafo = _carregar_grafo(caminho_grafo)
    intervalo_ms = max(1, intervalo_ms)
    fps = max(1, 1000 // intervalo_ms)
    animar_verificacao(
        grafo,
        layout=layout,
        titulo="Passo a passo da coloração (BFS)",
        mostrar=False,
        caminho_saida=destino,
        fps=fps,
        intervalo_ms=intervalo_ms,
    )


def main() -> None:
    pasta_imagens = BASE_DIR / "docs" / "imagens"
    pasta_imagens.mkdir(parents=True, exist_ok=True)

    grafo_bipartido = BASE_DIR / "exemplos" / "bipartido.txt"
    grafo_nao_bipartido = BASE_DIR / "exemplos" / "nao_bipartido.txt"

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
