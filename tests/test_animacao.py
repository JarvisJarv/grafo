import pathlib

import pytest
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from grafo.bipartido import GrafoBipartido
from grafo.visualizacao import (
    _ANIMACOES_ATIVAS,
    _registrar_animacao_ativa,
    animar_verificacao,
)


@pytest.fixture()
def grafo_simples() -> GrafoBipartido:
    grafo = GrafoBipartido()
    grafo.carregar_de_arquivo("exemplos/bipartido.txt")
    grafo.verificar_biparticao()
    return grafo


def test_animar_verificacao_exporta_gif(tmp_path: pathlib.Path, grafo_simples: GrafoBipartido) -> None:
    destino = tmp_path / "animacao.gif"
    animacao = animar_verificacao(
        grafo_simples,
        mostrar=False,
        caminho_saida=destino,
        fps=2,
        intervalo_ms=200,
    )

    assert destino.exists(), "O arquivo GIF deve ser gerado"
    assert animacao.event_source is not None


def test_registro_animacao_remove_ao_fechar() -> None:
    _ANIMACOES_ATIVAS.clear()
    figura = Figure()
    FigureCanvasAgg(figura)

    class _DummyAnim:
        event_source = object()

    animacao = _DummyAnim()
    _registrar_animacao_ativa(figura, animacao)  # type: ignore[arg-type]

    assert animacao in _ANIMACOES_ATIVAS

    figura.canvas.callbacks.process("close_event", None)

    assert animacao not in _ANIMACOES_ATIVAS
