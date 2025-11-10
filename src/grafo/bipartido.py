"""Implementação de um grafo bipartido com verificação de coloração."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from .io import DadosGrafo, carregar_de_arquivo

Cor = int
Aresta = Tuple[str, str]


@dataclass
class ResultadoBiparticao:
    """Resultado da verificação de bipartição."""

    eh_bipartido: bool
    cores: Dict[str, Cor]
    conflitos: List[Aresta]

    def particao(self, cor: Cor) -> Set[str]:
        """Retorna o conjunto de vértices coloridos com a cor indicada."""

        return {vertice for vertice, cor_atribuida in self.cores.items() if cor_atribuida == cor}

    @property
    def particoes(self) -> Tuple[Set[str], Set[str]]:
        """Retorna as duas partições identificadas (cores 0 e 1)."""

        return self.particao(0), self.particao(1)


class GrafoBipartido:
    """Representação de um grafo não direcionado com verificação de bipartição."""

    def __init__(self) -> None:
        self._vertices: Set[str] = set()
        self._arestas: List[Aresta] = []
        self._adjacencia: Dict[str, Set[str]] = {}
        self._resultado: Optional[ResultadoBiparticao] = None

    @property
    def vertices(self) -> Set[str]:
        return set(self._vertices)

    @property
    def arestas(self) -> List[Aresta]:
        return list(self._arestas)

    @property
    def resultado(self) -> Optional[ResultadoBiparticao]:
        """Retorna o último resultado calculado."""

        return self._resultado

    def carregar(self, dados: DadosGrafo) -> None:
        """Carrega o grafo a partir de ``DadosGrafo``."""

        self._vertices = set(dados.vertices)
        self._arestas = list(dados.arestas)
        self._adjacencia = {vertice: set() for vertice in self._vertices}

        for origem, destino in self._arestas:
            self._adjacencia.setdefault(origem, set()).add(destino)
            self._adjacencia.setdefault(destino, set()).add(origem)

        self._resultado = None

    def carregar_de_arquivo(self, caminho: str) -> None:
        """Lê o grafo de um arquivo texto."""

        dados = carregar_de_arquivo(caminho)
        self.carregar(dados)

    def verificar_biparticao(self) -> ResultadoBiparticao:
        """Executa um BFS para colorir o grafo e verifica conflitos."""

        cores: Dict[str, Cor] = {}
        conflitos: List[Aresta] = []

        for vertice in self._vertices:
            if vertice in cores:
                continue

            cores[vertice] = 0
            fila: deque[str] = deque([vertice])

            while fila:
                atual = fila.popleft()
                cor_atual = cores[atual]
                cor_oposta = 1 - cor_atual

                for vizinho in self._adjacencia.get(atual, set()):
                    if vizinho not in cores:
                        cores[vizinho] = cor_oposta
                        fila.append(vizinho)
                    elif cores[vizinho] == cor_atual:
                        origem, destino = sorted((atual, vizinho))
                        conflito: Aresta = (origem, destino)
                        if conflito not in conflitos:
                            conflitos.append(conflito)

        eh_bipartido = not conflitos
        self._resultado = ResultadoBiparticao(eh_bipartido=eh_bipartido, cores=cores, conflitos=conflitos)
        return self._resultado

    def obter_particoes(self) -> Tuple[Set[str], Set[str]]:
        """Retorna as partições, executando a verificação se necessário."""

        if self._resultado is None:
            self.verificar_biparticao()

        assert self._resultado is not None
        return self._resultado.particoes

    def listar_conflitos(self) -> List[Aresta]:
        """Retorna a lista de conflitos identificados na última execução."""

        if self._resultado is None:
            self.verificar_biparticao()

        assert self._resultado is not None
        return list(self._resultado.conflitos)

    def como_dicionario(self) -> Dict[str, object]:
        """Interface simples para expor o resultado do algoritmo."""

        if self._resultado is None:
            self.verificar_biparticao()

        assert self._resultado is not None
        particao_a, particao_b = self._resultado.particoes
        return {
            "eh_bipartido": self._resultado.eh_bipartido,
            "cores": self._resultado.cores,
            "particao_a": sorted(particao_a),
            "particao_b": sorted(particao_b),
            "conflitos": [list(conflito) for conflito in self._resultado.conflitos],
        }
