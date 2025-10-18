#!/usr/bin/env python3
"""
hill_climbing_8rainhas.py

Implementação do problema das 8 Rainhas usando Hill Climbing com:
 - movimentos laterais permitidos (limitados)
 - reinícios aleatórios (random-restart)
 - métricas: tempo, iterações, reinícios, sucesso

Modo de uso:
    python hill_climbing_8rainhas.py

Parâmetros editáveis no bloco __main__ ou via CLI (argparse).
"""

from typing import List, Tuple, Optional
import random
import time
import argparse
import matplotlib.pyplot as plt
import numpy as np

def plot_board(board, title="Tabuleiro 8 Rainhas", save_as: str = None):
    """
    Visualiza o tabuleiro das 8 rainhas com matplotlib.
    Usa quadrados brancos e pretos alternados e ícones de rainhas.
    """
    n = len(board)
    board_pattern = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            board_pattern[i, j] = (i + j) % 2

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(board_pattern, cmap="gray", vmin=0, vmax=1)

    # adiciona as rainhas
    for col, row in enumerate(board):
        ax.text(
            col, row, "♛", ha="center", va="center",
            fontsize=28, color="crimson"
        )

    # ajustes visuais
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(range(1, n + 1))
    ax.set_yticklabels(range(1, n + 1))
    ax.set_title(title, fontsize=14)
    ax.tick_params(left=False, bottom=False, labelsize=10)
    plt.gca().invert_yaxis()
    plt.tight_layout()

    if save_as:
        plt.savefig(save_as, dpi=300)
    plt.show()

Board = List[int]  # board[col] = row (0..7)


def random_board(n: int = 8) -> Board:
    """Gera um tabuleiro aleatório: uma rainha por coluna, linha sorteada."""
    return [random.randrange(n) for _ in range(n)]


def conflicts(board: Board) -> int:
    """Retorna o número de pares de rainhas em conflito (0 = solução)."""
    n = len(board)
    c = 0
    for i in range(n):
        for j in range(i + 1, n):
            if board[i] == board[j] or abs(board[i] - board[j]) == abs(i - j):
                c += 1
    return c


def neighbors(board: Board) -> List[Tuple[Board, Tuple[int, int]]]:
    """
    Gera todos os vizinhos por mover cada rainha em sua coluna para
    outra linha. Retorna lista de (novo_tabuleiro, (coluna, nova_linha)).
    """
    n = len(board)
    neighs = []
    for col in range(n):
        for row in range(n):
            if row != board[col]:
                nb = board.copy()
                nb[col] = row
                neighs.append((nb, (col, row)))
    return neighs


def best_neighbors(board: Board) -> Tuple[int, List[Tuple[Board, Tuple[int, int]]]]:
    """
    Calcula o melhor valor de conflito entre vizinhos e retorna (melhor_valor, lista_de_melhores).
    """
    neighs = neighbors(board)
    best_val = None
    best_list = []
    for nb, mv in neighs:
        val = conflicts(nb)
        if best_val is None or val < best_val:
            best_val = val
            best_list = [(nb, mv)]
        elif val == best_val:
            best_list.append((nb, mv))
    return best_val if best_val is not None else conflicts(board), best_list


def hill_climb(
    start: Board,
    max_iters: int = 1000,
    allow_sideways: bool = True,
    max_sideways: int = 100,
    random_tiebreak: bool = True
) -> Tuple[Board, bool, int]:
    """
    Executa Hill Climbing a partir de 'start'.
    Retorna (final_board, success_flag, iters_used).
    - success_flag = True se conflicts(final_board) == 0
    - permite movimentos laterais (quando best_val == current_val) até max_sideways vezes
    - random_tiebreak: pega um vizinho aleatório entre os melhores (útil para escapar simetrias)
    """
    current = start.copy()
    current_val = conflicts(current)
    if current_val == 0:
        return current, True, 0

    sideways_used = 0
    iters = 0
    for iters in range(1, max_iters + 1):
        best_val, best_list = best_neighbors(current)

        # Se houver melhora estrita
        if best_val < current_val:
            nxt, mv = random.choice(best_list) if random_tiebreak and len(best_list) > 1 else best_list[0]
            current, current_val = nxt, best_val
            # reset sideways counter -- opcional (mantemos como 0 para contar novos plateau)
            sideways_used = 0
        elif best_val == current_val and allow_sideways and sideways_used < max_sideways and len(best_list) > 0:
            # aceitar movimento lateral (plateau)
            nxt, mv = random.choice(best_list) if random_tiebreak and len(best_list) > 1 else best_list[0]
            current, current_val = nxt, best_val
            sideways_used += 1
        else:
            # Não há melhoria e não podemos mover lateralmente -> máximo local ou plateau saturado
            break

        if current_val == 0:
            return current, True, iters

    return current, (current_val == 0), iters


def random_restart(
    n: int = 8,
    max_restarts: int = 100,
    max_iters: int = 1000,
    allow_sideways: bool = True,
    max_sideways: int = 100,
    seed: Optional[int] = None
) -> dict:
    """
    Wrapper que aplica hill_climb com reinícios aleatórios até encontrar solução ou esgotar reinícios.
    Retorna dicionário com estatísticas e a solução (se encontrada).
    """
    if seed is not None:
        random.seed(seed)

    start_time = time.perf_counter()
    total_iters = 0

    for restart in range(max_restarts + 1):
        start_board = random_board(n)
        final, success, iters = hill_climb(
            start_board,
            max_iters=max_iters,
            allow_sideways=allow_sideways,
            max_sideways=max_sideways
        )
        total_iters += iters
        if success:
            elapsed = time.perf_counter() - start_time
            return {
                "success": True,
                "solution": final,
                "conflicts": 0,
                "restarts_used": restart,
                "total_iterations": total_iters,
                "time_s": elapsed
            }
    elapsed = time.perf_counter() - start_time
    # se saiu do loop sem sucesso, retorna melhor encontrado (podemos também retornar melhor global)
    return {
        "success": False,
        "solution": final,
        "conflicts": conflicts(final),
        "restarts_used": max_restarts,
        "total_iterations": total_iters,
        "time_s": elapsed
    }


def pretty_print_board(board: Board) -> None:
    """Imprime o tabuleiro em ASCII ('.' vazio, 'Q' rainha)."""
    n = len(board)
    for r in range(n):
        row = ""
        for c in range(n):
            row += "Q " if board[c] == r else ". "
        print(row)
    print(f"Conflicts: {conflicts(board)}")
    print("Board vector (col->row):", board)


def run_example():
    """Executa alguns testes exemplares e imprime resultados."""
    print("Exemplo: Hill Climbing 8-Rainhas (random-restart)\n")
    params = {
        "n": 8,
        "max_restarts": 50,
        "max_iters": 1000,
        "allow_sideways": True,
        "max_sideways": 100,
        "seed": 42
    }
    print("Parâmetros:", params)
    res = random_restart(**params)
    print("\nResultado:")
    print("Sucesso:", res["success"])
    print("Reinícios usados:", res["restarts_used"])
    print("Iterações totais:", res["total_iterations"])
    print("Tempo (s): {:.6f}".format(res["time_s"]))
    print("Conflitos finais:", res["conflicts"])
    if res["solution"]:
        pretty_print_board(res["solution"])
        plot_board(res["solution"], title="Solução encontrada pelo Hill Climbing")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hill Climbing - 8 Rainhas (com random-restart)")
    parser.add_argument("--restarts", type=int, default=50, help="máx. reinícios aleatórios")
    parser.add_argument("--iters", type=int, default=1000, help="máx. iterações por tentativa")
    parser.add_argument("--sideways", type=int, default=100, help="máx. movimentos laterais permitidos (0 desativa)")
    parser.add_argument("--seed", type=int, default=42, help="semente para reprodutibilidade (use None para aleatório)")
    parser.add_argument("--trials", type=int, default=10, help="executa múltiplas execuções para estatísticas")
    parser.add_argument("--no-display", action="store_true", help="não tentar abrir janela gráfica (apenas salvar imagens)")
    args = parser.parse_args()

    # parâmetros
    allow_sideways = args.sideways > 0
    max_sideways = args.sideways

    # executar várias trials e apresentar estatísticas simples
    successes = 0
    times = []
    iters_list = []
    restarts_list = []

    for t in range(args.trials):
        seed = args.seed + t if args.seed is not None else None
        r = random_restart(
            n=8,
            max_restarts=args.restarts,
            max_iters=args.iters,
            allow_sideways=allow_sideways,
            max_sideways=max_sideways,
            seed=seed
        )
        successes += 1 if r["success"] else 0
        times.append(r["time_s"])
        iters_list.append(r["total_iterations"])
        restarts_list.append(r["restarts_used"])
        print(f"Trial {t+1}: success={r['success']} restarts={r['restarts_used']} iters={r['total_iterations']} time={r['time_s']:.6f}s")

        # Se tiver solução: salvar figura e (tentar) mostrar
        if r["success"] and r.get("solution"):
            fn = f"solucao_trial_{t+1}.png"
            # tenta salvar e (se permitido) mostrar a janela gráfica
            try:
                plot_board(r["solution"], title=f"Solução - Trial {t+1}", save_as=fn)
                print(f"Figura salva em: {fn}")
                if args.no_display:
                    # já salvou; não tenta abrir GUI
                    plt.close('all')
                else:
                    # em alguns ambientes (headless) plt.show() pode falhar silenciosamente
                    # mas a chamada abaixo tenta abrir a janela gráfica
                    try:
                        plt.show(block=True)
                    except Exception:
                        # ambiente sem display -> já temos a imagem salva
                        pass
            except Exception as e:
                print("Erro ao gerar/mostrar figura:", e)

    print("\nResumo ({} trials):".format(args.trials))
    print("Sucesso total:", successes)
    print("Taxa de sucesso: {:.2f}%".format(100.0 * successes / args.trials))
    if times:
        print("Tempo médio (s): {:.6f}".format(sum(times) / len(times)))
    if iters_list:
        print("Iterações médias:", sum(iters_list) / len(iters_list))
    if restarts_list:
        print("Reinícios médios:", sum(restarts_list) / len(restarts_list))
