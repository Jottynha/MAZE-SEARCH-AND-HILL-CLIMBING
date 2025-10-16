import collections  # Utilizado para deque, usado em BFS e DFS
import heapq # Utilizado para filas de prioridade
from typing import List, Tuple, Callable, Set, Deque, Dict, Optional # Utilizado para tipagem como Lista, Tupla...
from .maze import Maze, Pos # Pos é uma tupla (linha, coluna) e Maze é a classe do labirinto
import random # Utilizado para setar semente
import numpy as np # Utilizado para setar semente (se necessário)

def set_seed(seed: int = 42) -> None:
    """
    -> Fixar semente pseudo-aleatória para reprodutibilidade.
    -> Chame set_seed(42) (ou outro valor) ANTES de gerar mazes ou executar os testes.
    -> Isso define random.seed e (se disponível) numpy.random.seed.
    """
    random.seed(seed)
    if np is not None:
        np.random.seed(seed)

# ===
# Estruturas Auxiliares
# ===

class Node:
    """
    -> Representa um nó na árvore de busca com as métricas necessárias.
    """
    def __init__(self, state: Pos, parent: 'Node' = None, action: str = None,
                 path_cost: float = 0.0, h_score: float = 0.0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost  # g(n)
        self.h_score = h_score      # h(n)
        self.f_score = path_cost + h_score  # f(n) = g + h
    def __lt__(self, other: 'Node'):
        return self.f_score < other.f_score # utilizado pela heapq; compara por f_score

# Tipo do retorno: (transições de caminho, custo, memória_máxima, nós_expandidos, solução_encontrada)
SearchResult = Tuple[List[Tuple[Pos, Pos]], float, int, int, bool]

def reconstruct_path(node: Node) -> List[Tuple[Pos, Pos]]:
    """
    -> Reconstrói o caminho como uma lista de transições de estado (de, para).
    """
    path_transitions: List[Tuple[Pos, Pos]] = []
    current = node
    while current.parent is not None:
        path_transitions.append((current.parent.state, current.state))
        current = current.parent
    path_transitions.reverse()
    return path_transitions

def _get_start_goal(maze: Maze) -> Tuple[Optional[Pos], Optional[Pos]]:
    """
    -> Tenta obter start e goal do objeto maze (várias convenções).
    """
    start = getattr(maze, 'start', None)
    goal = getattr(maze, 'goal', None)
    if start is None:
        start = getattr(maze, 'start_pos', None)
    if goal is None:
        goal = getattr(maze, 'goal_pos', None)
    return start, goal

def _ensure_goal_test_and_step_cost(maze: Maze):
    """
    -> Garante que maze tem os 'métodos' esperados por search.py:
      -> maze.goal_test(pos) -> bool
      -> maze.step_cost(s, a, n) -> float
    -> Se não existir, cria versões padrão:
      -> goal_test: p == maze.goal
      -> step_cost: custo unitário 1.0
    """
    if not hasattr(maze, 'goal_test'):
        def goal_test(p: Pos) -> bool:
            g = getattr(maze, 'goal', None)
            return g is not None and p == g
        maze.goal_test = goal_test  
    if not hasattr(maze, 'step_cost'):
        def step_cost(s: Pos, a: str, n: Pos) -> float:
            return 1.0
        maze.step_cost = step_cost  

# ===
# Algoritmos de Busca Não Informada (BFS e DFS)
# ===

def bfs(maze: Maze) -> SearchResult:
    """Busca em Largura (BFS)."""
    start, goal = _get_start_goal(maze)
    if start is None or goal is None:
        raise ValueError("Maze precisa ter 'start' e 'goal' definidos antes de executar bfs().")
    _ensure_goal_test_and_step_cost(maze)

    start_node = Node(start, path_cost=0.0)
    frontier: Deque[Node] = collections.deque([start_node])
    explored: Set[Pos] = {start}
    nodes_expanded = 0
    max_memory = 1
    exploration_path: List[Tuple[Pos, Pos]] = []

    while frontier:
        current_node = frontier.popleft()
        nodes_expanded += 1
        if maze.goal_test(current_node.state):
            # Retorna o caminho de exploração completo (igual para todos métodos de busca)
            return (exploration_path, current_node.path_cost, max_memory, nodes_expanded, True)
        for action in maze.actions(current_node.state):
            next_state = maze.result(current_node.state, action)
            if next_state not in explored:
                exploration_path.append((current_node.state, next_state))
                cost = maze.step_cost(current_node.state, action, next_state)
                new_node = Node(next_state, current_node, action, current_node.path_cost + cost)
                explored.add(next_state)
                frontier.append(new_node)
                max_memory = max(max_memory, len(frontier) + len(explored))
    return (exploration_path, 0.0, max_memory, nodes_expanded, False)

def dfs(maze: Maze) -> SearchResult:
    """Busca em Profundidade (DFS)."""
    start, goal = _get_start_goal(maze)
    if start is None or goal is None:
        raise ValueError("Maze precisa ter 'start' e 'goal' definidos antes de executar dfs().")
    _ensure_goal_test_and_step_cost(maze)

    start_node = Node(start, path_cost=0.0)
    frontier: Deque[Node] = collections.deque([start_node])
    explored: Set[Pos] = {start}
    nodes_expanded = 0
    max_memory = 1
    exploration_path: List[Tuple[Pos, Pos]] = []

    while frontier:
        current_node = frontier.pop()
        nodes_expanded += 1
        if maze.goal_test(current_node.state):
            return (exploration_path, current_node.path_cost, max_memory, nodes_expanded, True)
        # Expansão em ordem reversa para manter comportamento LIFO consistente
        for action in reversed(maze.actions(current_node.state)):
            next_state = maze.result(current_node.state, action)
            if next_state not in explored:
                exploration_path.append((current_node.state, next_state))
                cost = maze.step_cost(current_node.state, action, next_state)
                new_node = Node(next_state, current_node, action, current_node.path_cost + cost)
                explored.add(next_state)
                frontier.append(new_node)
                max_memory = max(max_memory, len(frontier) + len(explored))
    return (exploration_path, 0.0, max_memory, nodes_expanded, False)

# ===
# Algoritmos de Busca Informada (Gulosa e A*)
# ===

HeuristicFn = Callable[[Pos, Pos], float]

def greedy_search(maze: Maze, heuristic_fn: HeuristicFn) -> SearchResult:
    """Busca Gulosa (ordena só por h(n))."""
    start, goal = _get_start_goal(maze)
    if start is None or goal is None:
        raise ValueError("Maze precisa ter 'start' e 'goal' definidos antes de executar greedy_search().")
    _ensure_goal_test_and_step_cost(maze)

    h_start = heuristic_fn(start, goal)
    start_node = Node(start, path_cost=0.0, h_score=h_start)
    start_node.f_score = h_start  # na gulosa f = h
    frontier = [(start_node.f_score, 0, start_node)]
    counter = 1
    explored: Dict[Pos, float] = {start: start_node.f_score}
    nodes_expanded = 0
    max_memory = 1
    exploration_path: List[Tuple[Pos, Pos]] = []

    while frontier:
        _, _, current_node = heapq.heappop(frontier)
        nodes_expanded += 1
        if maze.goal_test(current_node.state): 
            return (exploration_path, current_node.path_cost, max_memory, nodes_expanded, True)
        for action in maze.actions(current_node.state):
            next_state = maze.result(current_node.state, action)
            cost = maze.step_cost(current_node.state, action, next_state)
            h_next = heuristic_fn(next_state, goal)
            new_node = Node(next_state, current_node, action, current_node.path_cost + cost, h_next)
            new_node.f_score = h_next
            if next_state not in explored or new_node.f_score < explored[next_state]:
                exploration_path.append((current_node.state, next_state))
                explored[next_state] = new_node.f_score
                heapq.heappush(frontier, (new_node.f_score, counter, new_node))
                counter += 1
                max_memory = max(max_memory, len(frontier) + len(explored))
    return (exploration_path, 0.0, max_memory, nodes_expanded, False)


def a_star_search(maze: Maze, heuristic_fn: HeuristicFn) -> SearchResult:
    """Busca A* (f = g + h)."""
    start, goal = _get_start_goal(maze)
    if start is None or goal is None:
        raise ValueError("Maze precisa ter 'start' e 'goal' definidos antes de executar a_star_search().")
    _ensure_goal_test_and_step_cost(maze)
    h_start = heuristic_fn(start, goal)
    start_node = Node(start, path_cost=0.0, h_score=h_start)
    start_node.f_score = start_node.path_cost + start_node.h_score
    frontier = [(start_node.f_score, 0, start_node)]
    counter = 1
    g_scores: Dict[Pos, float] = {start: 0.0}
    nodes_expanded = 0
    max_memory = 1
    exploration_path: List[Tuple[Pos, Pos]] = []
    while frontier:
        _, _, current_node = heapq.heappop(frontier)
        if current_node.path_cost > g_scores.get(current_node.state, float('inf')):
            continue
        nodes_expanded += 1
        if maze.goal_test(current_node.state):
            return (exploration_path, current_node.path_cost, max_memory, nodes_expanded, True)
        for action in maze.actions(current_node.state):
            next_state = maze.result(current_node.state, action)
            cost = maze.step_cost(current_node.state, action, next_state)
            tentative_g = current_node.path_cost + cost
            if tentative_g < g_scores.get(next_state, float('inf')):
                exploration_path.append((current_node.state, next_state))
                h_next = heuristic_fn(next_state, goal)
                new_node = Node(next_state, current_node, action, tentative_g, h_next)
                g_scores[next_state] = tentative_g
                heapq.heappush(frontier, (new_node.f_score, counter, new_node))
                counter += 1
                max_memory = max(max_memory, len(frontier) + len(g_scores))
    return (exploration_path, 0.0, max_memory, nodes_expanded, False)
