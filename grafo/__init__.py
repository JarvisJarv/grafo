"""Compatibilidade para importar o pacote diretamente a partir da raiz."""
from __future__ import annotations

from importlib import import_module
from pathlib import Path
from pkgutil import extend_path
import sys
from types import ModuleType

_RAIZ = Path(__file__).resolve().parents[1]
_SRC_DIR = _RAIZ / "src"
_SRC_GRAFO = _SRC_DIR / "grafo"

# Garante que ``src/`` esteja presente no ``sys.path`` quando o pacote
# for importado diretamente do repositório sem instalação prévia.
if _SRC_DIR.exists() and str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

# Permite que ``grafo.<submódulo>`` aponte para os arquivos reais dentro de ``src/``.
__path__ = extend_path(__path__, __name__)
if _SRC_GRAFO.exists():
    __path__.insert(0, str(_SRC_GRAFO))

# Reexporta os símbolos definidos no pacote real em ``src/grafo``.
_impl: ModuleType = import_module("src.grafo")
__all__ = getattr(_impl, "__all__", [])
for _nome in __all__:
    globals()[_nome] = getattr(_impl, _nome)

# Também propaga quaisquer atributos adicionais que não estejam em ``__all__``
# para manter compatibilidade com importações antigas.
for _chave, _valor in _impl.__dict__.items():
    if _chave.startswith("_") or _chave in globals():
        continue
    globals()[_chave] = _valor

# Remove variáveis internas do namespace do pacote público.
del ModuleType, import_module, Path, extend_path, sys, _RAIZ, _SRC_DIR, _SRC_GRAFO, _impl
