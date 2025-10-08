# main.py
import time
import os
from typing import List, Tuple, Callable, Any, Dict
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from src.maze import Maze
from src.heuristics import h_manhattan
from src.search import bfs, dfs, greedy_search, a_star_search, set_seed

SearchResult = Tuple[List[str], float, int, int, bool]

TESTS = [
    ("BFS (Não Informada)", bfs, None),
    ("DFS (Não Informada)", dfs, None),
    ("Gulosa (Manhattan)", lambda m: greedy_search(m, h_manhattan), h_manhattan),
    ("A* (Manhattan)", lambda m: a_star_search(m, h_manhattan), h_manhattan),
]

# Ajuste conforme seu labirinto — valor de referência para validar optimalidade.
COSTO_MINIMO_OTIMO = 5.0

def run_test(name: str, search_func: Callable[[Maze], SearchResult], maze: Maze) -> Dict[str, Any]:
    start_time = time.perf_counter()
    try:
        path, cost, max_memory, nodes_expanded, solution_found = search_func(maze)
        end_time = time.perf_counter()
        exec_time = end_time - start_time

        is_complete = solution_found
        is_optimal = solution_found and (abs(cost - COSTO_MINIMO_OTIMO) < 1e-6)

        # Formata caminho como string simples para saída (ações separadas por " -> ")
        caminho_str = " -> ".join(path) if path else "N/A"
        custo_str = f"{cost:.2f}" if solution_found else "N/A"

        return {
            "Algoritmo": name,
            "Tempo (s)": f"{exec_time:.6f}",
            "Max Memória (elementos)": max_memory,
            "Nós Expandidos": nodes_expanded,
            "Custo Solução": custo_str,
            "Completude": "SIM" if is_complete else "NÃO",
            "Optimalidade": "SIM" if is_optimal else "NÃO",
            # campos extra para o arquivo detalhado / análise
            "Caminho": caminho_str,
            "_raw_cost": cost if solution_found else None,
            "_found": solution_found,
            "_time": exec_time,               # campo numérico para plotagem
            "_path_length": len(path) if path else None
        }
    except Exception as e:
        return {
            "Algoritmo": name,
            "Tempo (s)": "ERRO",
            "Max Memória (elementos)": "ERRO",
            "Nós Expandidos": "ERRO",
            "Custo Solução": "ERRO",
            "Completude": "ERRO",
            "Optimalidade": "ERRO",
            "Caminho": "ERRO",
            "_error": str(e)
        }

def print_results(results: List[Dict[str, Any]], output_file: str = "medicoes_desempenho.txt"):
    # Prepare headers (não incluímos campos "privados" que começam com "_" na tabela)
    headers = [h for h in results[0].keys() if not h.startswith("_")]
    col_widths = {header: len(header) for header in headers}
    for result in results:
        for header in headers:
            col_widths[header] = max(col_widths[header], len(str(result.get(header, ""))))

    def format_row(data, is_header=False):
        return " | ".join(f"{str(data.get(header, '')).ljust(col_widths[header])}" for header in headers)

    output_lines = []
    output_lines.append("--- RESULTADOS DAS MEDIÇÕES DE DESEMPENHO (TRABALHO 1) ---")
    output_lines.append(f"Custo Mínimo Ótimo (Referência): {COSTO_MINIMO_OTIMO:.2f}")
    output_lines.append(format_row({h: h for h in headers}, is_header=True))
    output_lines.append("-" * (sum(col_widths.values()) + 3 * (len(headers) - 1)))
    for result in results:
        output_lines.append(format_row(result))
    output_lines.append("-" * (sum(col_widths.values()) + 3 * (len(headers) - 1)))

    # Seção detalhada: caminhos e custos encontrados por método
    output_lines.append("\n--- CAMINHOS E CUSTOS ENCONTRADOS (DETALHADO) ---")
    for result in results:
        nome = result.get("Algoritmo", "DESCONHECIDO")
        caminho = result.get("Caminho", "N/A")
        # pega custo raw se existir, senão usa o campo formatado
        raw_cost = result.get("_raw_cost", None)
        if raw_cost is not None:
            custo_text = f"{raw_cost:.2f}"
        else:
            custo_text = result.get("Custo Solução", "N/A")
        encontrado = "SIM" if result.get("_found", False) else "NÃO"
        output_lines.append(f"Algoritmo: {nome}")
        output_lines.append(f"  - Solução Encontrada: {encontrado}")
        output_lines.append(f"  - Custo: {custo_text}")
        output_lines.append(f"  - Caminho (ações): {caminho}")
        output_lines.append("")  # linha em branco entre métodos

    # Escreve em arquivo e também imprime no console
    full_output = "\n".join(output_lines)
    print(full_output)
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_output)
        print(f"\nResultados salvos em {output_file}")
    except Exception as e:
        print(f"Erro ao salvar resultados em {output_file}: {e}")

# --- Funções de plotagem das métricas (Barras preenchidas com pontos sobrepostos) ---

def _ensure_out_dir(out_dir: str):
    os.makedirs(out_dir, exist_ok=True)

def plot_metric_bars(df: pd.DataFrame, metric_key: str, display_name: str, out_dir: str = "bench_results") -> str:
    """
    Gera um gráfico de barras preenchidas comparando a média da 'metric_key' entre os métodos,
    com barras de erro (desvio padrão) e pontos individuais sobrepostos (jitter).
    - metric_key: coluna numérica no DataFrame (ex.: '_time', 'Max Memória (elementos)', '_raw_cost', '_path_length')
    - display_name: rótulo para o eixo y / título
    """
    _ensure_out_dir(out_dir)
    # converte para numérico forçando NaN em valores inválidos
    series_df = df[['Algoritmo', metric_key]].copy()
    series_df[metric_key] = pd.to_numeric(series_df[metric_key], errors='coerce')
    # filtrar apenas valores válidos
    series_df = series_df.dropna(subset=[metric_key])

    if series_df.empty:
        print(f"Aviso: Não há dados válidos para a métrica '{display_name}'. Nenhum gráfico será gerado.")
        return ""

    methods = sorted(series_df['Algoritmo'].unique())
    means = []
    stds = []
    counts = []
    values_per_method = []
    for m in methods:
        vals = series_df[series_df['Algoritmo'] == m][metric_key].values
        values_per_method.append(vals)
        means.append(np.mean(vals) if len(vals) > 0 else 0.0)
        stds.append(np.std(vals, ddof=0) if len(vals) > 0 else 0.0)
        counts.append(len(vals))

    x = np.arange(len(methods))
    width = 0.6

    plt.figure(figsize=(9, 6))
    # barras preenchidas (média) com barra de erro = std
    bars = plt.bar(x, means, width=width, yerr=stds, capsize=6, alpha=0.9)

    # adicionar rótulos de valor médio acima das barras
    for xi, mval in zip(x, means):
        plt.text(xi, mval, f"{mval:.3g}", ha='center', va='bottom', fontsize=9)

    # sobrepor pontos individuais (jitter horizontal para visualização)
    rng = np.random.default_rng(42)  # reprodutível
    for idx, vals in enumerate(values_per_method):
        if len(vals) == 0:
            continue
        jitter = rng.normal(loc=0.0, scale=0.05, size=len(vals))
        xs = np.full(len(vals), x[idx]) + jitter
        plt.scatter(xs, vals, alpha=0.7, edgecolors='k', linewidths=0.4, s=40)

    plt.xticks(x, methods, rotation=25)
    plt.title(f"Comparação de '{display_name}' entre métodos")
    plt.ylabel(display_name)
    plt.xlabel("Método de Busca")
    plt.tight_layout()

    filename = os.path.join(out_dir, f"compare_bar_{metric_key.strip('_')}.png")
    plt.savefig(filename)
    plt.close()
    print(f"Gráfico salvo: {filename}")
    return filename

def plot_all_metrics(results: List[Dict[str, Any]], out_dir: str = "bench_results") -> Dict[str, str]:
    """
    Converte results para DataFrame e gera gráficos para as métricas principais (barras preenchidas).
    Retorna um dicionário {metric_key: filepath}.
    """
    df = pd.DataFrame(results)
    files = {}
    metrics = [
        ('_time', 'Tempo (s)'),
        ('Max Memória (elementos)', 'Max Memória (elementos)'),
        ('Nós Expandidos', 'Nós Expandidos'),
        ('_raw_cost', 'Custo (bruto)'),
        ('_path_length', 'Comprimento do Caminho')
    ]
    for key, label in metrics:
        fpath = plot_metric_bars(df, key, label, out_dir=out_dir)
        if fpath:
            files[key] = fpath
    return files

def main():
    # FIXA A SEMENTE PARA REPRODUTIBILIDADE (chame antes de gerar/carregar mazes aleatórios)
    set_seed(42)

    lab_file = 'data/labirinto.txt'
    try:
        # Maze.from_file agora devolve (maze, start_pos?, goal_pos?) conforme seu main original
        maze, start_pos, goal_pos = Maze.from_file(lab_file)
    except Exception as e:
        print(f"ERRO CRÍTICO: Não foi possível carregar o labirinto. {e}")
        return

    # Anexa start/goal ao objeto maze para compatibilidade com search.py
    if start_pos is None or goal_pos is None:
        print("Start e/ou Goal não encontrados no ficheiro. Verifique o ficheiro de dados.")
        return
    maze.start = start_pos
    maze.goal = goal_pos

    # Define funções padrão exigidas por search.py (podem ser sobrescritas no Maze)
    if not hasattr(maze, 'goal_test'):
        maze.goal_test = lambda p: p == maze.goal  # type: ignore
    if not hasattr(maze, 'step_cost'):
        maze.step_cost = lambda s, a, n: 1.0  # type: ignore

    print(f"Labirinto carregado de {lab_file}. Início: {maze.start}, Fim: {maze.goal}")
    all_results = []
    for name, func, _ in TESTS:
        print(f"\nRodando teste: {name}...")
        result = run_test(name, func, maze)
        all_results.append(result)

    if all_results:
        print_results(all_results)

        # Gerar gráficos comparativos das métricas
        print("\nGerando gráficos comparativos das métricas...")
        files = plot_all_metrics(all_results, out_dir="bench_results")
        if files:
            print("Gráficos gerados:")
            for k, v in files.items():
                print(f"  - {k}: {v}")
        else:
            print("Nenhum gráfico gerado (dados insuficientes).")

if __name__ == "__main__":
    main()
