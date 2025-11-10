import pytest

from grafo.bipartido import GrafoBipartido
from grafo.io import carregar_de_iteravel
from grafo.visualizacao import preparar_desenho


@pytest.fixture()
def grafo_usuarios_filmes() -> GrafoBipartido:
    linhas = [
        "gabriel filme_mad_max",
        "gabriel filme_matrix",
        "marcelo filme_mad_max",
        "larissa filme_totoro",
    ]
    dados = carregar_de_iteravel(linhas)
    grafo = GrafoBipartido()
    grafo.carregar(dados)
    grafo.verificar_biparticao()
    return grafo


def test_layout_bipartido_posiciona_colunas(grafo_usuarios_filmes: GrafoBipartido) -> None:
    grafo_nx, posicoes, _, _, resultado = preparar_desenho(grafo_usuarios_filmes, layout="bipartido")

    particao_a, particao_b = resultado.particoes
    xs_a = {round(posicoes[vertice][0], 1) for vertice in particao_a}
    xs_b = {round(posicoes[vertice][0], 1) for vertice in particao_b}

    assert xs_a == {0.1}
    assert xs_b == {0.9}
    assert set(grafo_nx.nodes) == particao_a | particao_b


def test_adjacencias_retorna_copia(grafo_usuarios_filmes: GrafoBipartido) -> None:
    original = grafo_usuarios_filmes.adjacencias()
    any_vertex = next(iter(original))
    original[any_vertex].clear()

    # A estrutura interna do grafo não deve ser alterada ao modificar o retorno.
    outro = grafo_usuarios_filmes.adjacencias()
    assert outro[any_vertex], "A lista de vizinhos não deve refletir alterações externas"


def test_layout_flechas_herda_posicoes_do_bipartido(grafo_usuarios_filmes: GrafoBipartido) -> None:
    _, posicoes, _, _, resultado = preparar_desenho(grafo_usuarios_filmes, layout="flechas")

    particao_a, particao_b = resultado.particoes
    xs_a = {round(posicoes[vertice][0], 1) for vertice in particao_a}
    xs_b = {round(posicoes[vertice][0], 1) for vertice in particao_b}

    assert xs_a in ({0.1}, {0.9})
    assert xs_b in ({0.1}, {0.9})
    assert xs_a != xs_b
