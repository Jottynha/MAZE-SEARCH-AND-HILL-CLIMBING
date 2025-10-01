import collections # collections.deque: fila de duas pontas (eficiente para BFS).
import heapq # filas de prioridade usando a estrutura heap binária.
from typing import List, Tuple, Callable, Set, Deque, Dict
from .maze import Maze, Pos

# ===
# Estruturas Auxiliares
# ===

class Node:
    """Representa um nó na árvore de busca com as métricas necessárias."""
    def __init__(self, state: Pos, parent: 'Node' = None, action: str = None, path_cost: float = 0.0, h_score: float = 0.0):
        self.state = state          # A posição (r, c)
        self.parent = parent        # O nó que gerou este (papai)
        self.action = action        # Ação para chegar a este nó (da posição do pai)
        self.path_cost = path_cost  # g(n): Custo acumulado do início até este nó
        self.h_score = h_score      # h(n): Custo estimado (heurística) até o objetivo
        self.f_score = path_cost + h_score # f(n) = g(n) + h(n)
    # Permite comparação em Fila de Prioridade 
    # Compara por f_score (A*), ou h_score (Gulosa), ou path_cost (UCS)
    def __lt__(self, other: 'Node'):
        return self.f_score < other.f_score

# Estrutura do retorno da função de busca (a ser definida no documento):
# Tuple[path: List[str], cost: float, max_memory: int, nodes_expanded: int, solution_found: bool]
SearchResult = Tuple[List[str], float, int, int, bool]

def reconstruct_path(node: Node) -> List[str]:
    """Reconstrói a sequência de ações do nó final até o início."""
    path_actions: List[str] = []
    current = node
    while current.parent is not None:
        path_actions.append(current.action)
        current = current.parent
    path_actions.reverse()
    return path_actions

# ===
# Algoritmos de Busca Não Informada (BFS e DFS)
# ===

def bfs(maze: Maze) -> SearchResult:
    """Busca em Largura (BFS): Ótimo para custo unitário, Completo."""
    start_node = Node(maze.start)
    # FRONTEIRA: Fila (FIFO) para BFS (Usando deque como fila)
    frontier: Deque[Node] = collections.deque([start_node])
    # EXPLORADOS: Conjunto de estados visitados para evitar ciclos
    explored: Set[Pos] = {maze.start}
    nodes_expanded: int = 0
    max_memory: int = 1 # Fronteira + Explorados (inicial)
    while frontier:
        # Pega o primeiro nó (FIFO)
        current_node = frontier.popleft()
        nodes_expanded += 1
        # Teste de Objetivo (antes da expansão, típico de BFS)
        if maze.goal_test(current_node.state):
            path = reconstruct_path(current_node)
            return (path, current_node.path_cost, max_memory, nodes_expanded, True)
        # Expansão
        for action in maze.actions(current_node.state):
            next_state = maze.result(current_node.state, action)
            if next_state not in explored:
                cost = maze.step_cost(current_node.state, action, next_state)
                new_node = Node(next_state, current_node, action, current_node.path_cost + cost)
                explored.add(next_state)
                frontier.append(new_node)
                # Métrica de Memória: máximo de elementos simultaneamente
                max_memory = max(max_memory, len(frontier) + len(explored))
    # Não encontrou a solução
    return ([], 0.0, max_memory, nodes_expanded, False)

def dfs(maze: Maze) -> SearchResult:
    """Busca em Profundidade (DFS): Pode ser Não Ótimo e Incompleto em grafo."""
    start_node = Node(maze.start)
    # FRONTEIRA: Pilha (LIFO) para DFS (Usando deque, mas com append/pop)
    frontier: Deque[Node] = collections.deque([start_node]) 
    # EXPLORADOS: Conjunto de estados visitados
    explored: Set[Pos] = {maze.start}
    nodes_expanded: int = 0
    max_memory: int = 1 # Fronteira + Explorados (inicial)
    while frontier:
        # Pega o último nó (LIFO)
        current_node = frontier.pop()
        nodes_expanded += 1
        # Teste de Objetivo
        if maze.goal_test(current_node.state):
            path = reconstruct_path(current_node)
            return (path, current_node.path_cost, max_memory, nodes_expanded, True)
        # Expansão (Expansão reversa para manter a ordem LIFO)
        # OBS: A ordem das ações deve ser consistente.
        for action in reversed(maze.actions(current_node.state)):
            next_state = maze.result(current_node.state, action)
            if next_state not in explored:
                cost = maze.step_cost(current_node.state, action, next_state)
                new_node = Node(next_state, current_node, action, current_node.path_cost + cost)   
                explored.add(next_state)
                frontier.append(new_node)
                # Métrica de Memória
                max_memory = max(max_memory, len(frontier) + len(explored))
    return ([], 0.0, max_memory, nodes_expanded, False)

# ===
# Algoritmos de Busca Informada (Gulosa e A*)
# ===

# A função de heurística é injetada
HeuristicFn = Callable[[Pos, Pos], float] # Um tipo de função que recebe duas posições e devolve um float.
def greedy_search(maze: Maze, heuristic_fn: HeuristicFn) -> SearchResult:
    """Busca Gulosa: Ordena pela heurística h(n). Incompleto e Não Ótimo."""
    h_start = heuristic_fn(maze.start, maze.goal)
    start_node = Node(maze.start, h_score=h_start, path_cost=0.0)
    # Para Busca Gulosa, o f_score representa APENAS h(n)
    start_node.f_score = h_start 
    # FRONTEIRA: Fila de Prioridade 
    # Item na fila: (f_score, counter, node) - counter garante desempate estável
    frontier: List[Tuple[float, int, Node]] = [(start_node.f_score, 0, start_node)]
    counter = 1
    # EXPLORADOS: Apenas para verificar se o estado já foi expandido/está na fronteira
    explored: Dict[Pos, float] = {maze.start: start_node.f_score}
    nodes_expanded: int = 0
    max_memory: int = 1
    while frontier:
        # Pega o nó de menor f_score (h_score neste caso)
        _, _, current_node = heapq.heappop(frontier)
        nodes_expanded += 1
        # Teste de Objetivo
        if maze.goal_test(current_node.state):
            path = reconstruct_path(current_node)
            return (path, current_node.path_cost, max_memory, nodes_expanded, True)
        # Expansão
        for action in maze.actions(current_node.state):
            next_state = maze.result(current_node.state, action)
            cost = maze.step_cost(current_node.state, action, next_state)
            h_next = heuristic_fn(next_state, maze.goal)
            new_node = Node(next_state, current_node, action, current_node.path_cost + cost, h_next)
            # Para Gulosa, f(n) = h(n)
            new_node.f_score = h_next 
            if next_state not in explored or new_node.f_score < explored[next_state]:
                explored[next_state] = new_node.f_score
                heapq.heappush(frontier, (new_node.f_score, counter, new_node))
                counter += 1
                # Métrica de Memória
                max_memory = max(max_memory, len(frontier) + len(explored))
    return ([], 0.0, max_memory, nodes_expanded, False)


def a_star_search(maze: Maze, heuristic_fn: HeuristicFn) -> SearchResult:
    """Busca A*: Ordena por f(n) = g(n) + h(n). Completo e Ótimo (com h admissível/consistente)."""

    h_start = heuristic_fn(maze.start, maze.goal)
    start_node = Node(maze.start, h_score=h_start, path_cost=0.0)
    # f(n) = g(n) + h(n)
    start_node.f_score = start_node.path_cost + start_node.h_score    
    # FRONTEIRA: Fila de Prioridade 
    frontier: List[Tuple[float, int, Node]] = [(start_node.f_score, 0, start_node)]
    counter = 1
    # EXPLORADOS: Map de estados para o menor g(n) encontrado até aquele estado
    g_scores: Dict[Pos, float] = {maze.start: 0.0}
    nodes_expanded: int = 0
    max_memory: int = 1
    while frontier:
        # Pega o nó de menor f_score
        _, _, current_node = heapq.heappop(frontier)
        # Teste de Objetivo (ocorre na expansão, mas pode ser verificado aqui)
        if maze.goal_test(current_node.state):
            path = reconstruct_path(current_node)
            return (path, current_node.path_cost, max_memory, nodes_expanded, True)
        nodes_expanded += 1
        # Expansão
        for action in maze.actions(current_node.state):
            next_state = maze.result(current_node.state, action)
            cost = maze.step_cost(current_node.state, action, next_state)
            tentative_g_score = current_node.path_cost + cost
            # Se o novo caminho for melhor que o g(n) conhecido (ou se for a primeira vez)
            if next_state not in g_scores or tentative_g_score < g_scores[next_state]:
                h_next = heuristic_fn(next_state, maze.goal)
                new_node = Node(next_state, current_node, action, tentative_g_score, h_next)
                g_scores[next_state] = tentative_g_score
                heapq.heappush(frontier, (new_node.f_score, counter, new_node))
                counter += 1
                # Métrica de Memória
                # g_scores funciona como o conjunto de estados visitados/explorados
                max_memory = max(max_memory, len(frontier) + len(g_scores))
    
    return ([], 0.0, max_memory, nodes_expanded, False)