from pathlib import Path

import pytest

from grafo.io import carregar_de_arquivo

BASE_DIR = Path(__file__).resolve().parent.parent


def caminho(nome: str) -> Path:
    return BASE_DIR / "exemplos" / nome


def test_carregar_usuario_filme_equilibrado():
    dados = carregar_de_arquivo(caminho("usuario_filme_equilibrado.txt"))

    assert dados.vertices == {
        "usuaria_ana",
        "usuaria_bia",
        "usuario_caio",
        "filme_matriz",
        "filme_her",
        "filme_up",
    }
    assert len(dados.arestas) == 6
    assert dados.posicoes["usuaria_ana"] == (0.15, 0.85)
    assert dados.posicoes["filme_up"] == (0.80, 0.15)


def test_carregar_usuario_filme_tendencias():
    dados = carregar_de_arquivo(caminho("usuario_filme_tendencias.txt"))

    assert "usuario_fred" in dados.vertices
    assert len(dados.arestas) == 7
    # Posição definida com x/y separados
    assert dados.posicoes["usuario_duda"] == pytest.approx((0.12, 0.82))
    assert dados.posicoes["filme_amor_em_paris"] == pytest.approx((0.82, 0.46))
    # Vértice sem posição explícita não deve aparecer no mapeamento
    assert "usuario_fred" not in dados.posicoes


def test_compatibilidade_formato_antigo():
    dados = carregar_de_arquivo(caminho("bipartido.txt"))

    assert ("u", "v") in dados.arestas
    assert dados.posicoes == {}
