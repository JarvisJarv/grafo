"""Implementação de um grafo bipartido com verificação de coloração."""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Set, Tuple

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


@dataclass(frozen=True)
class PassoBiparticao:
    """Representa uma etapa da execução do algoritmo de bipartição."""

    descricao: str
    vertice_atual: Optional[str]
    fila: Sequence[str]
    cores: Dict[str, Cor]
    conflitos: List[Aresta]
    aresta_analisada: Optional[Aresta] = None


class GrafoBipartido:
    """Representação de um grafo não direcionado com verificação de bipartição."""

    def __init__(self) -> None:
        self._vertices: List[str] = []
        self._arestas: List[Aresta] = []
        self._adjacencia: Dict[str, Set[str]] = {}
        self._resultado: Optional[ResultadoBiparticao] = None
        self._posicoes: Dict[str, Tuple[float, float]] = {}
        self._atributos: Dict[str, Dict[str, str]] = {}

    @property
    def vertices(self) -> Set[str]:
        return set(self._vertices)

    @property
    def arestas(self) -> List[Aresta]:
        return list(self._arestas)

    def adjacencias(self) -> Dict[str, Set[str]]:
        """Retorna uma cópia do dicionário de adjacências."""

        return {vertice: set(vizinhos) for vertice, vizinhos in self._adjacencia.items()}

    @property
    def resultado(self) -> Optional[ResultadoBiparticao]:
        """Retorna o último resultado calculado."""

        return self._resultado

    @property
    def posicoes(self) -> Dict[str, Tuple[float, float]]:
        """Retorna um dicionário com posições opcionais dos vértices."""

        return dict(self._posicoes)

    def atributos(self) -> Dict[str, Dict[str, str]]:
        """Retorna uma cópia dos atributos associados a cada vértice."""

        return {vertice: dict(atributos) for vertice, atributos in self._atributos.items()}

    def carregar(self, dados: DadosGrafo) -> None:
        """Carrega o grafo a partir de ``DadosGrafo``."""

        self._vertices = sorted(dados.vertices)
        self._arestas = list(dados.arestas)
        self._adjacencia = {vertice: set() for vertice in self._vertices}
        self._posicoes = dict(dados.posicoes)
        self._atributos = {vertice: dict(dados.atributos.get(vertice, {})) for vertice in self._vertices}

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

        resultado, _ = self._executar_bfs(registrar_passos=False)
        return resultado

    def verificar_biparticao_com_passos(self) -> Tuple[ResultadoBiparticao, List[PassoBiparticao]]:
        """Executa o BFS registrando as etapas percorridas."""

        return self._executar_bfs(registrar_passos=True)

    def _executar_bfs(
        self, *, registrar_passos: bool
    ) -> Tuple[ResultadoBiparticao, List[PassoBiparticao]]:
        cores: Dict[str, Cor] = {}
        conflitos: List[Aresta] = []
        passos: List[PassoBiparticao] = []

        fila: deque[str] = deque()

        def registrar(descricao: str, vertice: Optional[str] = None, aresta: Optional[Aresta] = None) -> None:
            if not registrar_passos:
                return

            passos.append(
                PassoBiparticao(
                    descricao=descricao,
                    vertice_atual=vertice,
                    fila=list(fila),
                    cores=dict(cores),
                    conflitos=list(conflitos),
                    aresta_analisada=aresta,
                )
            )

        for vertice in self._vertices:
            if vertice in cores:
                continue

            cores[vertice] = 0
            fila.clear()
            fila.append(vertice)
            registrar(f"Iniciando componente a partir de {vertice}", vertice)

            while fila:
                atual = fila.popleft()
                registrar(f"Processando vértice {atual}", atual)
                cor_atual = cores[atual]
                cor_oposta = 1 - cor_atual

                for vizinho in sorted(self._adjacencia.get(atual, set())):
                    aresta = tuple(sorted((atual, vizinho)))
                    atributos_atual = self._atributos.get(atual, {})
                    atributos_vizinho = self._atributos.get(vizinho, {})
                    tipo_atual = atributos_atual.get("tipo", "").lower()
                    tipo_vizinho = atributos_vizinho.get("tipo", "").lower()
                    conflito_tipo = bool(tipo_atual and tipo_vizinho and tipo_atual == tipo_vizinho)

                    if vizinho not in cores:
                        cores[vizinho] = cor_oposta
                        fila.append(vizinho)
                        registrar(
                            f"Colorindo {vizinho} com a cor {cor_oposta} e adicionando à fila",
                            vertice=atual,
                            aresta=aresta,
                        )
                        if conflito_tipo:
                            if aresta not in conflitos:
                                conflitos.append(aresta)
                            registrar(
                                "Conflito de tipos detectado: "
                                f"{atual} ({atributos_atual.get('tipo', '—')}) — "
                                f"{vizinho} ({atributos_vizinho.get('tipo', '—')})",
                                vertice=atual,
                                aresta=aresta,
                            )
                    else:
                        conflito_biparticao = cores[vizinho] == cor_atual
                        if conflito_biparticao or conflito_tipo:
                            if aresta not in conflitos:
                                conflitos.append(aresta)
                            if conflito_tipo and not conflito_biparticao:
                                mensagem = (
                                    "Conflito de tipos detectado: "
                                    f"{atual} ({atributos_atual.get('tipo', '—')}) — "
                                    f"{vizinho} ({atributos_vizinho.get('tipo', '—')})"
                                )
                            elif conflito_tipo:
                                mensagem = (
                                    "Conflito detectado: cores iguais e tipos equivalentes em "
                                    f"{atual} — {vizinho}"
                                )
                            else:
                                mensagem = f"Conflito detectado em {atual} -- {vizinho}"
                            registrar(mensagem, vertice=atual, aresta=aresta)
                        else:
                            registrar(
                                f"Aresta {atual} -- {vizinho} respeita as cores",
                                vertice=atual,
                                aresta=aresta,
                            )

            registrar(f"Componente iniciado em {vertice} completamente processado")

        eh_bipartido = not conflitos
        resultado = ResultadoBiparticao(eh_bipartido=eh_bipartido, cores=cores, conflitos=conflitos)
        self._resultado = resultado

        registrar(
            "Verificação concluída: "
            + ("grafo bipartido sem conflitos" if eh_bipartido else "conflitos detectados"),
            vertice=None,
        )

        return resultado, passos

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
            "posicoes": {vertice: list(posicao) for vertice, posicao in self._posicoes.items()},
            "atributos": {vertice: dict(atributos) for vertice, atributos in self._atributos.items()},
        }

    def tipos_por_particao(self) -> Dict[int, str]:
        """Sugere rótulos para cada partição com base no atributo ``tipo``."""

        if self._resultado is None:
            self.verificar_biparticao()

        assert self._resultado is not None

        tipos_por_cor: Dict[int, List[str]] = {0: [], 1: []}
        for vertice, cor in self._resultado.cores.items():
            tipo = self._atributos.get(vertice, {}).get("tipo")
            if tipo:
                tipos_por_cor.setdefault(cor, []).append(tipo)

        resumo: Dict[int, str] = {}
        for cor, tipos in tipos_por_cor.items():
            if tipos:
                resumo[cor] = Counter(tipos).most_common(1)[0][0]
        return resumo
