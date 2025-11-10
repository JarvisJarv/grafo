"""CLI simples para verificar a bipartição de um grafo."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    # Permite executar ``python src/main.py`` ajustando o caminho para ``src/``.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from grafo.bipartido import GrafoBipartido
else:
    from .grafo.bipartido import GrafoBipartido


def main() -> None:
    parser = argparse.ArgumentParser(description="Verifica se um grafo é bipartido")
    parser.add_argument("arquivo", type=Path, help="Caminho para o arquivo com a lista de arestas")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Exibe o resultado completo em formato JSON",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Abre uma visualização gráfica com as partições e conflitos",
    )
    parser.add_argument(
        "--animar",
        action="store_true",
        help="Exibe a animação passo a passo do algoritmo de bipartição",
    )
    parser.add_argument(
        "--exportar-animacao",
        type=Path,
        help="Exporta a animação em MP4 ou GIF para o caminho informado",
    )
    parser.add_argument(
        "--layout",
        choices=("spring", "circular", "kamada_kawai", "bipartido", "flechas"),
        default="spring",
        help=(
            "Algoritmo de posicionamento dos vértices ao exibir o grafo. "
            "Use 'flechas' para gerar colunas com setas indicando as conexões."
        ),
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=1,
        help="Quadros por segundo ao animar ou exportar a execução",
    )
    args = parser.parse_args()

    if args.fps <= 0:
        parser.error("--fps deve ser maior que zero")

    grafo = GrafoBipartido()
    grafo.carregar_de_arquivo(args.arquivo)
    resultado = grafo.verificar_biparticao()

    if args.json:
        print(json.dumps(grafo.como_dicionario(), ensure_ascii=False, indent=2))
    else:
        particao_a, particao_b = resultado.particoes
        print("Grafo bipartido:" if resultado.eh_bipartido else "Grafo NÃO bipartido:")
        print(f"  Partição 0: {', '.join(sorted(particao_a)) or '∅'}")
        print(f"  Partição 1: {', '.join(sorted(particao_b)) or '∅'}")
        if resultado.conflitos:
            print("  Conflitos detectados:")
            for origem, destino in resultado.conflitos:
                print(f"    - {origem} -- {destino}")
        else:
            print("  Nenhum conflito detectado.")

    if args.plot:
        try:
            if __package__ in (None, ""):
                from grafo.visualizacao import exibir_grafo
            else:
                from .grafo.visualizacao import exibir_grafo

            exibir_grafo(grafo, layout=args.layout, titulo=f"Resultado para {args.arquivo}")
        except ImportError as exc:
            mensagem = (
                "Dependências de visualização não disponíveis. "
                "Instale 'matplotlib' e 'networkx' para utilizar --plot."
            )
            raise SystemExit(f"{mensagem}\nDetalhes: {exc}") from exc

    if args.animar or args.exportar_animacao:
        try:
            if __package__ in (None, ""):
                from grafo.visualizacao import animar_verificacao
            else:
                from .grafo.visualizacao import animar_verificacao

            animar_verificacao(
                grafo,
                layout=args.layout,
                titulo=f"Execução do algoritmo para {args.arquivo}",
                mostrar=args.animar,
                caminho_saida=str(args.exportar_animacao) if args.exportar_animacao else None,
                fps=args.fps,
            )
            if args.exportar_animacao:
                print(f"Animação exportada para {args.exportar_animacao}")
        except ImportError as exc:
            mensagem = (
                "Dependências de visualização não disponíveis. "
                "Instale 'matplotlib' e 'networkx' para utilizar --animar ou --exportar-animacao."
            )
            raise SystemExit(f"{mensagem}\nDetalhes: {exc}") from exc
        except RuntimeError as exc:
            raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
