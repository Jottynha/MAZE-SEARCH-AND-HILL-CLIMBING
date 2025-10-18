"""
hill_climbing.py

Hill Climbing com Random-Restart, coleta de métricas e geração de gráficos.

Uso:
    python hill_climbing.py --trials 50 --restarts 100 --seed 42
    python hill_climbing.py --vary-restarts 10 50 100 200 --trials 30 --seed 42

O script gera CSVs e PNGs com os gráficos.
"""
from typing import List, Dict, Any, Optional
import random
import time
import csv
import argparse
import statistics
import numpy as np
import matplotlib.pyplot as plt
import os

from eight_queens import random_board, conflicts

Board = List[int]


class HillClimber:
    def __init__(self, n: int = 8, max_iters: int = 1000, allow_sideways: bool = True, max_sideways: int = 100, random_tiebreak: bool = True):
        self.n = n
        self.max_iters = max_iters
        self.allow_sideways = allow_sideways
        self.max_sideways = max_sideways
        self.random_tiebreak = random_tiebreak

    def neighbors(self, board: Board):
        n = self.n
        for col in range(n):
            for row in range(n):
                if row != board[col]:
                    nb = board.copy()
                    nb[col] = row
                    yield nb, (col, row)

    def best_neighbors(self, board: Board):
        best_val = None
        best_list = []
        cur_conf = conflicts(board)
        for nb, mv in self.neighbors(board):
            val = conflicts(nb)
            if best_val is None or val < best_val:
                best_val = val
                best_list = [(nb, mv)]
            elif val == best_val:
                best_list.append((nb, mv))
        return best_val if best_val is not None else cur_conf, best_list

    def climb(self, start: Board) -> Dict[str, Any]:
        current = start.copy()
        current_val = conflicts(current)
        result = {"start": start, "final": current, "start_conflicts": current_val, "final_conflicts": current_val, "iters": 0, "success": current_val == 0, "used_sideways": 0}
        if current_val == 0:
            return result

        sideways_used = 0
        for it in range(1, self.max_iters + 1):
            best_val, best_list = self.best_neighbors(current)

            if best_val < current_val:
                nxt, mv = (random.choice(best_list) if self.random_tiebreak and len(best_list) > 1 else best_list[0])
                current, current_val = nxt, best_val
                sideways_used = 0
            elif best_val == current_val and self.allow_sideways and sideways_used < self.max_sideways and len(best_list) > 0:
                nxt, mv = (random.choice(best_list) if self.random_tiebreak and len(best_list) > 1 else best_list[0])
                current, current_val = nxt, best_val
                sideways_used += 1
            else:
                result.update({"final": current, "final_conflicts": current_val, "iters": it, "success": (current_val == 0), "used_sideways": sideways_used})
                return result

            if current_val == 0:
                result.update({"final": current, "final_conflicts": 0, "iters": it, "success": True, "used_sideways": sideways_used})
                return result

        result.update({"final": current, "final_conflicts": current_val, "iters": self.max_iters, "success": (current_val == 0), "used_sideways": sideways_used})
        return result


class RandomRestartRunner:
    def __init__(self, climber: HillClimber, max_restarts: int = 100, seed: Optional[int] = None):
        self.climber = climber
        self.max_restarts = max_restarts
        self.seed = seed

    def run_once(self) -> Dict[str, Any]:
        start_time = time.perf_counter()
        total_iters = 0
        best = None
        best_conf = None

        for restart in range(self.max_restarts):
            start_board = random_board(self.climber.n)
            res = self.climber.climb(start_board)
            total_iters += res["iters"]

            if best is None or res["final_conflicts"] < best_conf:
                best = res["final"]
                best_conf = res["final_conflicts"]

            if res["success"]:
                elapsed = time.perf_counter() - start_time
                return {
                    "success": True,
                    "solution": res["final"],
                    "conflicts": 0,
                    "restarts_used": restart + 1,
                    "total_iterations": total_iters,
                    "time_s": elapsed,
                    "start_conflicts": res.get("start_conflicts"),
                    "final_conflicts": res.get("final_conflicts"),
                    "used_sideways": res.get("used_sideways"),
                }

        elapsed = time.perf_counter() - start_time
        return {
            "success": False,
            "solution": best,
            "conflicts": best_conf,
            "restarts_used": self.max_restarts,
            "total_iterations": total_iters,
            "time_s": elapsed,
            "start_conflicts": None,
            "final_conflicts": best_conf,
            "used_sideways": None,
        }


# ---------- plotting helpers ----------

def plot_success_rate(x_values, y_values, xlabel, ylabel, title, save_as=None, show: bool = False):
    plt.figure()
    plt.plot(x_values, y_values, marker="o")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    if save_as:
        plt.savefig(save_as, dpi=200)
        plt.close()
    if show and not save_as:
        plt.show()


def boxplot_metric(metrics: List[float], label: str, title: str, save_as: Optional[str] = None, show: bool = False):
    plt.figure()
    plt.boxplot(metrics)
    plt.title(title)
    plt.ylabel(label)
    if save_as:
        plt.savefig(save_as, dpi=200)
        plt.close()
    if show and not save_as:
        plt.show()


def histogram_metric(metrics: List[float], bins: int, xlabel: str, title: str, save_as: Optional[str] = None, show: bool = False):
    plt.figure()
    plt.hist(metrics, bins=bins)
    plt.xlabel(xlabel)
    plt.title(title)
    if save_as:
        plt.savefig(save_as, dpi=200)
        plt.close()
    if show and not save_as:
        plt.show()
    plt.close()


def plot_board(board, title="Tabuleiro 8 Rainhas", save_as: str = None, show: bool = False):
    """
    Visualiza o tabuleiro das 8 rainhas com matplotlib.
    Usa quadrados brancos e pretos alternados e ícones de rainhas.
    """
    n = len(board)
    board_pattern = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if (i + j) % 2 == 0:
                board_pattern[i, j] = 0.8
            else:
                board_pattern[i, j] = 0.2

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
        plt.savefig(save_as, dpi=200)
    
    if show and not save_as:
        plt.show()
    
    plt.close(fig)


# ---------- experiments and CLI ----------

def run_trials(climber: HillClimber, restarts: int, trials: int, seed: Optional[int] = None):
    runner = RandomRestartRunner(climber=climber, max_restarts=restarts, seed=seed)
    results = []
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    for t in range(trials):
        r = runner.run_once()
        results.append(r)
    return results


def save_results_csv(filename: str, results: List[Dict[str, Any]]):
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['success','restarts_used','total_iterations','time_s','conflicts','start_conflicts','final_conflicts','used_sideways'])
        writer.writeheader()
        for r in results:
            writer.writerow({k: r.get(k) for k in writer.fieldnames})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--trials', type=int, default=30)
    parser.add_argument('--restarts', type=int, default=100)
    parser.add_argument('--iters', type=int, default=1000)
    parser.add_argument('--sideways', type=int, default=100)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--vary-restarts', nargs='*', type=int, help='Lista de valores de restart para experimentar (ex: 10 50 100)')
    parser.add_argument('--no-display', action='store_true', help='Não mostrar janelas de plot (salvar apenas PNGs).')
    args = parser.parse_args()

    output_dir = "output"
    csv_dir = os.path.join(output_dir, "csv")
    boxplot_dir = os.path.join(output_dir, "boxplot")
    histogram_dir = os.path.join(output_dir, "histogram")
    plots_dir = os.path.join(output_dir, "plots")
    solutions_dir = os.path.join(output_dir, "solutions")
    for d in [csv_dir, boxplot_dir, histogram_dir, plots_dir, solutions_dir]:
        if not os.path.exists(d):
            os.makedirs(d)

    climber = HillClimber(n=8, max_iters=args.iters, allow_sideways=(args.sideways>0), max_sideways=args.sideways)

    show_plots = not args.no_display

    if args.vary_restarts:
        summary = []
        for r_idx, r_val in enumerate(args.vary_restarts):
            print(f"Running trials for restarts={r_val} ...")
            results = run_trials(climber, restarts=r_val, trials=args.trials, seed=args.seed)
            save_results_csv(os.path.join(csv_dir, f'results_restarts_{r_val}.csv'), results)

            for t_idx, res in enumerate(results):
                if res['success']:
                    board = res['solution']
                    plot_board(
                        board,
                        title=f"Solução (restarts={r_val}, trial={t_idx+1})",
                        save_as=os.path.join(solutions_dir, f'solution_restarts_{r_val}_trial_{t_idx+1}.png'),
                        show=False
                    )

            times = [x['time_s'] for x in results]
            succ = sum(1 for x in results if x['success'])
            summary.append((r_val, succ/args.trials, statistics.mean(times)))

            boxplot_metric(times, 'Tempo (s)', f'Tempo (s) — restarts={r_val}', save_as=os.path.join(boxplot_dir, f'box_times_restarts_{r_val}.png'), show=show_plots)
            histogram_metric([x['total_iterations'] for x in results], bins=20, xlabel='Iterações', title=f'Hist Iterações — restarts={r_val}', save_as=os.path.join(histogram_dir, f'hist_iters_restarts_{r_val}.png'), show=show_plots)

        xs = [s[0] for s in summary]
        ys = [s[1]*100 for s in summary]
        plot_success_rate(xs, ys, xlabel='max_restarts', ylabel='% Sucesso', title='Taxa de sucesso vs max_restarts', save_as=os.path.join(plots_dir, 'success_vs_restarts.png'), show=show_plots)

        print('Experimentos concluídos. CSVs e PNGs salvos.')

    else:
        print(f'Running {args.trials} trials with restarts={args.restarts} ...')
        results = run_trials(climber, restarts=args.restarts, trials=args.trials, seed=args.seed)
        save_results_csv(os.path.join(csv_dir, 'results_summary.csv'), results)

        for t_idx, res in enumerate(results):
            if res['success']:
                board = res['solution']
                plot_board(
                    board,
                    title=f"Solução (trial={t_idx+1})",
                    save_as=os.path.join(solutions_dir, f'solution_trial_{t_idx+1}.png'),
                    show=False
                )

        times = [x['time_s'] for x in results]
        boxplot_metric(times, 'Tempo (s)', 'Boxplot de tempos', save_as=os.path.join(boxplot_dir, 'box_times.png'), show=show_plots)
        histogram_metric([x['total_iterations'] for x in results], bins=20, xlabel='Iterações', title='Hist Iterações', save_as=os.path.join(histogram_dir, 'hist_iters.png'), show=show_plots)

        print('Experimento concluído. CSV e PNGs salvos.')


if __name__ == '__main__':
    main()
