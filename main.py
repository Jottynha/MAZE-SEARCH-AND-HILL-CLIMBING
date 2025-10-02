# main.py
import time
from typing import List, Tuple, Callable, Any, Dict
from src.maze import Maze
from src.heuristics import h_manhattan
from src.search import bfs, dfs, greedy_search, a_star_search

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
            # campos extra para o arquivo detalhado
            "Caminho": caminho_str,
            "_raw_cost": cost if solution_found else None,
            "_found": solution_found
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

def main():
    lab_file = 'data/labirinto.txt'
    try:
        # Maze.from_file agora devolve (maze, start_pos?, goal_pos?)
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

if __name__ == "__main__":
    main()
