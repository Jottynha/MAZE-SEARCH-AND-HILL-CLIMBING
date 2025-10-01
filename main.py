import time
from typing import List, Tuple, Callable, Any, Dict
from src.maze import Maze
from src.heuristics import h_manhattan 
from src.search import bfs, dfs, greedy_search, a_star_search 

# Estrutura do retorno da função de busca:
# Tuple[path: List[str], cost: float, max_memory: int, nodes_expanded: int, solution_found: bool]
SearchResult = Tuple[List[str], float, int, int, bool]
TESTS = [
    # (Nome do Algoritmo, Função de Busca, Heurística (None se não informada))
    # (i) Dois Não Informados
    ("BFS (Não Informada)", bfs, None),
    ("DFS (Não Informada)", dfs, None), # CUIDADO: DFS pode não ser ótimo ou completo.
    # (ii) Gulosa vs A*
    ("Gulosa (Manhattan)", lambda m: greedy_search(m, h_manhattan), h_manhattan),
    ("A* (Manhattan)", lambda m: a_star_search(m, h_manhattan), h_manhattan),
]

# --- Variável Chave para Análise de Optimalidade ---
# Custo mínimo ótimo conhecido para o labirinto de teste (alterar depois aiii aiiii).
# rodando a busca A* ou BFS/UCS e verificando o custo mínimo retornado.
COSTO_MINIMO_OTIMO = 5.0 # <--- SUBSTITUIR ESTE VALOR PELO CUSTO MÍNIMO REAL! (SIM, ESTÁ ESCRITO ERRADO)

def run_test(name: str, search_func: Callable[[Maze], SearchResult], maze: Maze) -> Dict[str, Any]:
    """Executa um algoritmo de busca e mede suas métricas de desempenho."""
    start_time = time.perf_counter()
    try:
        # A função de busca deve retornar as 5 métricas
        path, cost, max_memory, nodes_expanded, solution_found = search_func(maze)
        end_time = time.perf_counter()
        exec_time = end_time - start_time
        # ---------------------------------------------------------
        # ANÁLISE DE MÉTRICAS (Completude e Optimalidade)
        # ---------------------------------------------------------
        # Completude: O algoritmo encontrou a solução?
        is_complete = solution_found
        # Optimalidade: A solução tem custo mínimo? (Requer COSTO_MINIMO_OTIMO)
        # Usamos uma pequena tolerância (1e-6) para comparação de floats
        is_optimal = solution_found and (abs(cost - COSTO_MINIMO_OTIMO) < 1e-6)
        # O BFS é ótimo para custo unitário, e A* com h. admissível é ótimo.
        if "DFS" in name or "Gulosa" in name:
             # DFS e Gulosa geralmente não são ótimos.
             is_optimal_expected = False
        else:
             is_optimal_expected = True # BFS e A* com h. admissível devem ser ótimos
        return {
            "Algoritmo": name,
            "Tempo (s)": f"{exec_time:.6f}",
            "Max Memória (elementos)": max_memory,
            "Nós Expandidos": nodes_expanded,
            "Custo Solução": f"{cost:.2f}" if solution_found else "N/A",
            "Completude": "SIM" if is_complete else "NÃO",
            "Optimalidade": "SIM" if is_optimal else "NÃO",
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
        }


def print_results(results: List[Dict[str, Any]], output_file: str = "medicoes_desempenho.txt"):
    """Imprime os resultados em formato de tabela e salva em arquivo."""
    # Define as chaves na ordem desejada
    headers = list(results[0].keys())
    # Calcula a largura de cada coluna
    col_widths = {header: len(header) for header in headers}
    for result in results:
        for header in headers:
            col_widths[header] = max(col_widths[header], len(str(result.get(header, ""))))
    def format_row(data, is_header=False):
        row = " | ".join(
            f"{str(data[header]).ljust(col_widths[header])}" for header in headers
        )
        return row
    output = []
    output.append("--- RESULTADOS DAS MEDIÇÕES DE DESEMPENHO (TRABALHO 1) ---")
    output.append(f"Custo Mínimo Ótimo (Referência): {COSTO_MINIMO_OTIMO:.2f}")
    output.append(format_row({h: h for h in headers}, is_header=True))
    output.append("-" * (sum(col_widths.values()) + 3 * (len(headers) - 1)))
    for result in results:
        output.append(format_row(result))
    output.append("-" * (sum(col_widths.values()) + 3 * (len(headers) - 1)))
    print("\n".join(output))
    with open(output_file, 'w') as f:
        f.write("\n".join(output))
        print(f"\nResultados salvos em {output_file}")

def main():
    lab_file = 'data/labirinto.txt'
    try:
        maze = Maze.from_file(lab_file)
        print(f"Labirinto carregado de {lab_file}. Início: {maze.start}, Fim: {maze.goal}")
    except Exception as e:
        print(f"ERRO CRÍTICO: Não foi possível carregar o labirinto. {e}")
        return

    all_results = []

    for name, func, _ in TESTS:
        print(f"\nRodando teste: {name}...")
        result = run_test(name, func, maze)
        all_results.append(result)
        
    if all_results:
        print_results(all_results)
        
        
if __name__ == "__main__":
    main()