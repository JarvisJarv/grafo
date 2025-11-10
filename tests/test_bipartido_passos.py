"""Testes para a captura de passos do algoritmo de bipartição."""
from grafo.bipartido import GrafoBipartido, PassoBiparticao
from grafo.io import DadosGrafo, carregar_de_iteravel


def _construir_grafo(vertices, arestas) -> GrafoBipartido:
    grafo = GrafoBipartido()
    grafo.carregar(DadosGrafo(vertices=set(vertices), arestas=list(arestas), posicoes={}))
    return grafo


def test_verificar_biparticao_com_passos_sem_conflito() -> None:
    grafo = _construir_grafo({"A", "B", "C"}, [("A", "B"), ("B", "C")])

    resultado, passos = grafo.verificar_biparticao_com_passos()

    assert resultado.eh_bipartido
    assert resultado.conflitos == []
    assert len(passos) >= 2

    descricoes = [passo.descricao for passo in passos]
    assert any("Iniciando componente" in descricao for descricao in descricoes)
    assert descricoes[-1].startswith("Verificação concluída")

    # As filas registradas não devem compartilhar referência
    filas = [passo.fila for passo in passos]
    assert all(isinstance(passo, PassoBiparticao) for passo in passos)
    assert all(isinstance(fila, list) for fila in filas)
    assert all(filas[i] is not filas[i + 1] for i in range(len(filas) - 1))


def test_verificar_biparticao_com_passos_com_conflito() -> None:
    grafo = _construir_grafo({"A", "B", "C"}, [("A", "B"), ("B", "C"), ("C", "A")])

    resultado, passos = grafo.verificar_biparticao_com_passos()

    assert not resultado.eh_bipartido
    assert {tuple(sorted(conflito)) for conflito in resultado.conflitos} == {("B", "C")}

    descricoes = [passo.descricao for passo in passos]
    assert any("Conflito detectado" in descricao for descricao in descricoes)
    ultimo_passo = passos[-1]
    assert "conflitos detectados" in ultimo_passo.descricao


def test_conflito_de_tipo_detectado() -> None:
    linhas = [
        "[vertices]",
        "Gabriel tipo=pessoa",
        "Marcelo tipo=pessoa",
        "Moana tipo=filme",
        "[arestas]",
        "Gabriel Moana",
        "Marcelo Gabriel",
    ]
    dados = carregar_de_iteravel(linhas)
    grafo = GrafoBipartido()
    grafo.carregar(dados)

    resultado = grafo.verificar_biparticao()

    assert not resultado.eh_bipartido
    assert {tuple(sorted(conflito)) for conflito in resultado.conflitos} == {("Gabriel", "Marcelo")}
