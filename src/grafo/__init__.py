"""Pacote principal com utilidades para verificação de grafos bipartidos."""

from .bipartido import GrafoBipartido, PassoBiparticao, ResultadoBiparticao
from .io import DadosGrafo, carregar_de_arquivo, carregar_de_iteravel

__all__ = [
    "GrafoBipartido",
    "PassoBiparticao",
    "ResultadoBiparticao",
    "DadosGrafo",
    "carregar_de_arquivo",
    "carregar_de_iteravel",
]
