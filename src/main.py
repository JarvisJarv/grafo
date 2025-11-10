"""CLI simples para verificar a bipartição de um grafo."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from grafo.bipartido import GrafoBipartido


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
        "--layout",
        choices=("spring", "circular", "kamada_kawai"),
        default="spring",
        help="Algoritmo de posicionamento dos vértices ao exibir o grafo",
    )
    args = parser.parse_args()

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
            from grafo.visualizacao import exibir_grafo

            exibir_grafo(grafo, layout=args.layout, titulo=f"Resultado para {args.arquivo}")
        except ImportError as exc:
            mensagem = (
                "Dependências de visualização não disponíveis. "
                "Instale 'matplotlib' e 'networkx' para utilizar --plot."
            )
            raise SystemExit(f"{mensagem}\nDetalhes: {exc}") from exc


if __name__ == "__main__":
    main()
