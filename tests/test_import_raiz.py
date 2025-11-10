import importlib
import importlib.util
import sys
from pathlib import Path


def test_importando_pacote_da_raiz(monkeypatch):
    raiz = Path(__file__).resolve().parents[1]
    src_dir = raiz / "src"

    novo_path = [str(raiz)]
    for entrada in sys.path:
        try:
            caminho = Path(entrada).resolve()
        except Exception:
            novo_path.append(entrada)
            continue
        if caminho == src_dir.resolve():
            continue
        novo_path.append(entrada)

    monkeypatch.setattr(sys, "path", novo_path)

    for chave in [modulo for modulo in sys.modules if modulo == "grafo" or modulo.startswith("grafo.")]:
        sys.modules.pop(chave)

    pacote = importlib.import_module("grafo")
    assert hasattr(pacote, "GrafoBipartido")

    spec = importlib.util.find_spec("grafo.interface")
    assert spec is not None

