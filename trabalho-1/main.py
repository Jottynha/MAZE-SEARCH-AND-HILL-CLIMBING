import time # Utilizado para temporização
import os # Utilizado para criar diretório de saída
from typing import List, Tuple, Callable, Any, Dict
import pandas as pd # Utilizado para manipulação de dados 
import matplotlib.pyplot as plt # Utilizado para plotagem de gráficos de comparação
import numpy as np 

from src.maze import Maze
from src.heuristics import h_manhattan, h_euclidiana
from src.search import bfs, dfs, greedy_search, a_star_search, set_seed

SearchResult = Tuple[List[Tuple[Any, Any]], float, int, int, bool]

TESTS = [
    ("BFS (Não Informada)",     lambda m: bfs(m),                             None,        'uninformed'),
    ("DFS (Não Informada)",     lambda m: dfs(m),                             None,        'uninformed'),

    ("Gulosa (Manhattan)",      lambda m: greedy_search(m, h_manhattan),      'Manhattan', 'informed'),
    ("Gulosa (Euclidiana)",     lambda m: greedy_search(m, h_euclidiana),     'Euclidiana','informed'),
    ("A* (Manhattan)",          lambda m: a_star_search(m, h_manhattan),      'Manhattan', 'informed'),
    ("A* (Euclidiana)",         lambda m: a_star_search(m, h_euclidiana),     'Euclidiana','informed'),
]

# -> Valor de referência para validar optimalidade.
CUSTO_MINIMO_OTIMO = 10.0

def run_test(name: str, search_func: Callable[[Maze], SearchResult], maze: Maze,
             group: str, heuristic_name: str | None) -> Dict[str, Any]:
    start_time = time.perf_counter()
    try:
        path, cost, max_memory, nodes_expanded, solution_found = search_func(maze)
        end_time = time.perf_counter()
        exec_time = end_time - start_time
        is_complete = solution_found
        is_optimal = solution_found and (abs(cost - CUSTO_MINIMO_OTIMO) < 1e-6)
        # Formata caminho como string simples para saída (transições de posição)
        caminho_str = " -> ".join([f"{p[0]}-{p[1]}" for p in path]) if path else "N/A"
        custo_str = f"{cost:.2f}" if solution_found else "N/A"
        return {
            "Algoritmo": name,
            "Tempo (s)": f"{exec_time:.6f}",
            "Max Memória (elementos)": max_memory,
            "Nós Expandidos": nodes_expanded,
            "Custo Solução": custo_str,
            "Completude": "SIM" if is_complete else "NÃO",
            "Optimalidade": "SIM" if is_optimal else "NÃO",
            # campos extra para o arquivo detalhado/análise
            "Caminho": caminho_str,
            "_raw_cost": cost if solution_found else float('nan'),
            "_time": exec_time,
            "_path_length": len(path) if path else 0,
            # metadados de filtro
            "_group": group,                 # 'Não Informado' | 'informado'
            "_heuristic": heuristic_name,    # nenhum | 'manhattan' | 'euclidiana'
            "_found": solution_found,
        }
    except Exception as e:
        return {
            "Algoritmo": name,
            "Tempo (s)": "ERRO",
            "Max Memória (elementos)": float('nan'),
            "Nós Expandidos": float('nan'),
            "Custo Solução": "ERRO",
            "Completude": "ERRO",
            "Optimalidade": "ERRO",
            "Caminho": "ERRO",
            "_error": str(e),
            "_raw_cost": float('nan'),
            "_time": float('nan'),
            "_path_length": float('nan'),
            "_group": group,
            "_heuristic": heuristic_name,
            "_found": False,
        }

def print_results(results: List[Dict[str, Any]], output_file: str = "medicoes_desempenho.txt"):
    headers = [h for h in results[0].keys() if not h.startswith("_")]
    col_widths = {header: len(header) for header in headers}
    for r in results:
        for h in headers:
            col_widths[h] = max(col_widths[h], len(str(r.get(h, ""))))

    def format_row(data):
        return " | ".join(f"{str(data.get(h, '')).ljust(col_widths[h])}" for h in headers)

    lines = []
    lines.append("--- RESULTADOS DAS MEDIÇÕES DE DESEMPENHO (BUSCAS NÃO-INFORMADAS E INFORMADAS) ---")
    lines.append(f"Custo Mínimo Ótimo (Referência): {CUSTO_MINIMO_OTIMO:.2f}")
    lines.append(format_row({h: h for h in headers}))
    lines.append("-" * (sum(col_widths.values()) + 3 * (len(headers) - 1)))
    for r in results:
        lines.append(format_row(r))
    lines.append("-" * (sum(col_widths.values()) + 3 * (len(headers) - 1)))
    lines.append("\n--- CAMINHOS E CUSTOS ENCONTRADOS (DETALHADO) ---")
    for r in results:
        nome = r.get("Algoritmo", "DESCONHECIDO")
        caminho = r.get("Caminho", "N/A")
        raw_cost = r.get("_raw_cost", np.nan)
        custo_text = f"{raw_cost:.2f}" if not (isinstance(raw_cost, float) and np.isnan(raw_cost)) else r.get("Custo Solução", "N/A")
        encontrado = "SIM" if r.get("_found", False) else "NÃO"
        lines.append(f"Algoritmo: {nome}")
        lines.append(f"  - Solução Encontrada: {encontrado}")
        lines.append(f"  - Custo: {custo_text}")
        lines.append(f"  - Caminho (ações): {caminho}")
        lines.append("")

    text = "\n".join(lines)
    print(text)
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"\nResultados salvos em {output_file}")
    except Exception as e:
        print(f"Erro ao salvar resultados em {output_file}: {e}")

# ===
# Funções de plotagem das métricas  
# ===

def _ensure_out_dir(path: str):
    os.makedirs(path, exist_ok=True)

def _plot_metric_bars(df: pd.DataFrame, metric_key: str, display_name: str, out_path: str) -> str:
    """
    -> Gera um gráfico de barras preenchidas comparando a média da 'metric_key' entre os métodos,
    -> Com barras de erro (desvio padrão) e pontos individuais sobrepostos (jitter).
     -> metric_key: coluna numérica no DataFrame (ex.: '_time', 'Max Memória (elementos)', '_raw_cost', '_path_length')
     -> display_name: rótulo para o eixo y / título
    """
    _ensure_out_dir(out_path)
    data = df[['Algoritmo', metric_key]].copy()
    data[metric_key] = pd.to_numeric(data[metric_key], errors='coerce')
    data = data.dropna(subset=[metric_key])

    if data.empty:
        print(f"Aviso: sem dados válidos para '{display_name}' em {out_path}.")
        return ""

    methods = list(data['Algoritmo'].unique())
    means, stds, values_per_method = [], [], []
    for m in methods:
        vals = data[data['Algoritmo'] == m][metric_key].values
        values_per_method.append(vals)
        means.append(np.mean(vals))
        stds.append(np.std(vals, ddof=0))

    x = np.arange(len(methods))
    plt.figure(figsize=(9, 6))
    plt.bar(x, means, width=0.6, yerr=stds, capsize=6, alpha=0.9)
    for xi, mval in zip(x, means):
        plt.text(xi, mval, f"{mval:.3g}", ha='center', va='bottom', fontsize=9)
    rng = np.random.default_rng(42)
    for idx, vals in enumerate(values_per_method):
        if len(vals) == 0: continue
        jitter = rng.normal(loc=0.0, scale=0.05, size=len(vals))
        xs = np.full(len(vals), x[idx]) + jitter
        plt.scatter(xs, vals, alpha=0.7, edgecolors='k', linewidths=0.4, s=40)

    plt.xticks(x, methods, rotation=25)
    plt.title(f"Comparação de '{display_name}'")
    plt.ylabel(display_name)
    plt.xlabel("Método de Busca")
    plt.tight_layout()

    filename = os.path.join(out_path, f"compare_bar_{metric_key.strip('_')}.png")
    plt.savefig(filename)
    plt.close()
    print(f"Gráfico salvo: {filename}")
    return filename

def plot_all_metrics(results: List[Dict[str, Any]], base_out_dir: str = "bench_results") -> Dict[str, Dict[str, str]]:
    """
    Gera gráficos para TODAS as métricas em DOIS conjuntos:
      1) 'uninformed' -> apenas BFS/DFS
      2) 'informed'   -> Gulosa/A* com Manhattan e Euclidiana
    Retorna dict:
      {
        'uninformed': {metric_key: filepath, ...},
        'informed':   {metric_key: filepath, ...}
      }
    """
    df = pd.DataFrame(results)
    uninformed_df = df[df["_group"] == "uninformed"].copy()
    informed_df   = df[df["_group"] == "informed"].copy()

    outputs = {'uninformed': {}, 'informed': {}}
    metrics = [
        ('_time', 'Tempo (s)'),
        ('Max Memória (elementos)', 'Max Memória (elementos)'),
        ('Nós Expandidos', 'Nós Expandidos'),
        ('_raw_cost', 'Custo (bruto)'),
        ('_path_length', 'Comprimento do Caminho'),
    ]

    # gráficos para não informadas
    out_dir_uninf = os.path.join(base_out_dir, "uninformed")
    for key, label in metrics:
        f = _plot_metric_bars(uninformed_df, key, label, out_dir_uninf)
        if f: outputs['uninformed'][key] = f

    # gráficos para informadas
    out_dir_inf = os.path.join(base_out_dir, "informed")
    for key, label in metrics:
        f = _plot_metric_bars(informed_df, key, label, out_dir_inf)
        if f: outputs['informed'][key] = f

    return outputs

def main():
    # FIXA A SEMENTE PARA REPRODUTIBILIDADE (chamada obrigatória antes de gerar/carregar labirintos aleatórios)
    set_seed(42)
    lab_file = 'trabalho-1/data/labirinto.txt'
    try:
        maze, start_pos, goal_pos = Maze.from_file(lab_file)
    except Exception as e:
        print(f"ERRO CRÍTICO: Não foi possível carregar o labirinto. {e}")
        return

    if start_pos is None or goal_pos is None:
        print("Start e/ou Goal não encontrados no ficheiro. Verifique o ficheiro de dados.")
        return

    maze.start = start_pos
    maze.goal = goal_pos
    if not hasattr(maze, 'goal_test'):
        maze.goal_test = lambda p: p == maze.goal  # type: ignore
    if not hasattr(maze, 'step_cost'):
        maze.step_cost = lambda s, a, n: 1.0       # type: ignore

    print(f"Labirinto carregado de {lab_file}. Início: {maze.start}, Fim: {maze.goal}")

    all_results = []
    for name, func, heuristic_name, group in TESTS:
        print(f"\nRodando teste: {name}...")
        all_results.append(run_test(name, func, maze, group, heuristic_name))

    if all_results:
        print_results(all_results)
        print("\nGerando gráficos comparativos das métricas...")
        files_by_group = plot_all_metrics(all_results, base_out_dir="trabalho-1/bench_results")
        for gname, files in files_by_group.items():
            if files:
                print(f"Gráficos gerados para '{gname}':")
                for k, v in files.items():
                    print(f"  - {k}: {v}")
            else:
                print(f"Nenhum gráfico gerado para '{gname}' (dados insuficientes).")

if __name__ == "__main__":
    main()
