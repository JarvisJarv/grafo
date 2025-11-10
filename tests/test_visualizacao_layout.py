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

    particao_0, particao_1 = resultado.particoes
    xs_particao_0 = {round(posicoes[vertice][0], 1) for vertice in particao_0}
    xs_particao_1 = {round(posicoes[vertice][0], 1) for vertice in particao_1}

    assert xs_particao_1 == {0.1}
    assert xs_particao_0 == {0.9}
    assert set(grafo_nx.nodes) == particao_0 | particao_1


def test_adjacencias_retorna_copia(grafo_usuarios_filmes: GrafoBipartido) -> None:
    original = grafo_usuarios_filmes.adjacencias()
    any_vertex = next(iter(original))
    original[any_vertex].clear()

    # A estrutura interna do grafo não deve ser alterada ao modificar o retorno.
    outro = grafo_usuarios_filmes.adjacencias()
    assert outro[any_vertex], "A lista de vizinhos não deve refletir alterações externas"


def test_layout_flechas_herda_posicoes_do_bipartido(grafo_usuarios_filmes: GrafoBipartido) -> None:
    _, posicoes, _, _, resultado = preparar_desenho(grafo_usuarios_filmes, layout="flechas")

    particao_0, particao_1 = resultado.particoes
    xs_particao_0 = {round(posicoes[vertice][0], 1) for vertice in particao_0}
    xs_particao_1 = {round(posicoes[vertice][0], 1) for vertice in particao_1}

    assert xs_particao_1 in ({0.1}, {0.9})
    assert xs_particao_0 in ({0.1}, {0.9})
    assert xs_particao_1 != xs_particao_0


def test_relacionamentos_formatados_prioriza_usuarios(
    grafo_usuarios_filmes: GrafoBipartido,
) -> None:
    relacoes = grafo_usuarios_filmes.relacionamentos_formatados()

    assert relacoes == [
        "gabriel x filme_mad_max",
        "gabriel x filme_matrix",
        "marcelo x filme_mad_max",
        "larissa x filme_totoro",
    ]
