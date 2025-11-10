"""Compatibilidade para importar ``grafo`` diretamente do diretório raiz.

Este módulo encaminha o carregamento para o pacote real localizado em
``src/grafo``. Dessa forma, comandos como ``python -m grafo.interface``
funcionam mesmo sem instalar o projeto como dependência.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_PACOTE_REAL = Path(__file__).resolve().parent.parent / "src" / "grafo"

if not _PACOTE_REAL.exists():  # pragma: no cover - ambiente inconsistente
    raise ModuleNotFoundError("Não foi possível localizar 'src/grafo' para carregamento do pacote")

_spec = importlib.util.spec_from_file_location(
    __name__,
    _PACOTE_REAL / "__init__.py",
    submodule_search_locations=[str(_PACOTE_REAL)],
)

if _spec is None or _spec.loader is None:  # pragma: no cover - falha inesperada
    raise ModuleNotFoundError("Não foi possível inicializar o pacote 'grafo'")

_mod = importlib.util.module_from_spec(_spec)
sys.modules[__name__] = _mod
_spec.loader.exec_module(_mod)
