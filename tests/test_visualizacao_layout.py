import pytest

from grafo.bipartido import GrafoBipartido
from grafo.io import carregar_de_iteravel
from grafo.visualizacao import preparar_desenho


@pytest.fixture()
def grafo_usuarios_filmes() -> GrafoBipartido:
    linhas = [
        "Gabriel x Mad Max",
        "Gabriel x Matrix",
        "Marcelo x Mad Max",
        "Larissa x Meu Vizinho Totoro",
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


def test_cores_de_arestas_refletem_particoes(grafo_usuarios_filmes: GrafoBipartido) -> None:
    _, _, _, cores_arestas, _ = preparar_desenho(grafo_usuarios_filmes, layout="bipartido")

    assert all(cor.startswith("#") and len(cor) == 7 for cor in cores_arestas)
    assert "#e74c3c" not in cores_arestas
    assert len(set(cores_arestas)) >= 2


def test_conflitos_coloridos_em_vermelho() -> None:
    linhas = [
        "Gabriel x Moana",
        "Moana x Marcelo",
        "Marcelo x Gabriel",
    ]
    dados = carregar_de_iteravel(linhas)
    grafo = GrafoBipartido()
    grafo.carregar(dados)
    grafo.verificar_biparticao()

    _, _, _, cores_arestas, resultado = preparar_desenho(grafo, layout="bipartido")

    assert not resultado.eh_bipartido
    assert "#e74c3c" in cores_arestas
