# src/search.py
import collections  # deque
import heapq
from typing import List, Tuple, Callable, Set, Deque, Dict, Optional
from .maze import Maze, Pos

# ===
# Estruturas Auxiliares
# ===

class Node:
    """Representa um nó na árvore de busca com as métricas necessárias."""
    def __init__(self, state: Pos, parent: 'Node' = None, action: str = None,
                 path_cost: float = 0.0, h_score: float = 0.0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost  # g(n)
        self.h_score = h_score      # h(n)
        self.f_score = path_cost + h_score  # f(n) = g + h

    def __lt__(self, other: 'Node'):
        # utilizado pela heapq; compara por f_score
        return self.f_score < other.f_score

# Tipo do retorno: (path_actions, cost, max_memory, nodes_expanded, solution_found)
SearchResult = Tuple[List[str], float, int, int, bool]

def reconstruct_path(node: Node) -> List[str]:
    """Reconstrói a sequência de ações do nó final até o início (lista de ações)."""
    path_actions: List[str] = []
    current = node
    while current.parent is not None:
        path_actions.append(current.action)
        current = current.parent
    path_actions.reverse()
    return path_actions

# --- Helpers para compatibilidade com o Maze atual ---
def _get_start_goal(maze: Maze) -> Tuple[Optional[Pos], Optional[Pos]]:
    """Tenta obter start e goal do objeto maze (várias convenções)."""
    start = getattr(maze, 'start', None)
    goal = getattr(maze, 'goal', None)
    # nomes alternativos possíveis
    if start is None:
        start = getattr(maze, 'start_pos', None)
    if goal is None:
        goal = getattr(maze, 'goal_pos', None)
    return start, goal

def _ensure_goal_test_and_step_cost(maze: Maze):
    """
    Garante que maze tem os 'métodos' esperados por search.py:
      - maze.goal_test(pos) -> bool
      - maze.step_cost(s, a, n) -> float
    Se não existir, cria versões padrão:
      - goal_test: p == maze.goal
      - step_cost: custo unitário 1.0
    """
    if not hasattr(maze, 'goal_test'):
        def goal_test(p: Pos) -> bool:
            g = getattr(maze, 'goal', None)
            return g is not None and p == g
        maze.goal_test = goal_test  # type: ignore
    if not hasattr(maze, 'step_cost'):
        def step_cost(s: Pos, a: str, n: Pos) -> float:
            return 1.0
        maze.step_cost = step_cost  # type: ignore

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

    while frontier:
        current_node = frontier.popleft()
        nodes_expanded += 1
        if maze.goal_test(current_node.state):
            path = reconstruct_path(current_node)
            return (path, current_node.path_cost, max_memory, nodes_expanded, True)
        for action in maze.actions(current_node.state):
            next_state = maze.result(current_node.state, action)
            if next_state not in explored:
                cost = maze.step_cost(current_node.state, action, next_state)
                new_node = Node(next_state, current_node, action, current_node.path_cost + cost)
                explored.add(next_state)
                frontier.append(new_node)
                max_memory = max(max_memory, len(frontier) + len(explored))
    return ([], 0.0, max_memory, nodes_expanded, False)

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

    while frontier:
        current_node = frontier.pop()
        nodes_expanded += 1
        if maze.goal_test(current_node.state):
            path = reconstruct_path(current_node)
            return (path, current_node.path_cost, max_memory, nodes_expanded, True)
        # expand in reversed order to keep consistent LIFO behaviour
        for action in reversed(maze.actions(current_node.state)):
            next_state = maze.result(current_node.state, action)
            if next_state not in explored:
                cost = maze.step_cost(current_node.state, action, next_state)
                new_node = Node(next_state, current_node, action, current_node.path_cost + cost)
                explored.add(next_state)
                frontier.append(new_node)
                max_memory = max(max_memory, len(frontier) + len(explored))
    return ([], 0.0, max_memory, nodes_expanded, False)

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

    while frontier:
        _, _, current_node = heapq.heappop(frontier)
        nodes_expanded += 1
        if maze.goal_test(current_node.state):
            path = reconstruct_path(current_node)
            return (path, current_node.path_cost, max_memory, nodes_expanded, True)
        for action in maze.actions(current_node.state):
            next_state = maze.result(current_node.state, action)
            cost = maze.step_cost(current_node.state, action, next_state)
            h_next = heuristic_fn(next_state, goal)
            new_node = Node(next_state, current_node, action, current_node.path_cost + cost, h_next)
            new_node.f_score = h_next
            if next_state not in explored or new_node.f_score < explored[next_state]:
                explored[next_state] = new_node.f_score
                heapq.heappush(frontier, (new_node.f_score, counter, new_node))
                counter += 1
                max_memory = max(max_memory, len(frontier) + len(explored))
    return ([], 0.0, max_memory, nodes_expanded, False)


def a_star_search(maze: Maze, heuristic_fn: HeuristicFn) -> SearchResult:
    """A* (f = g + h)."""
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

    while frontier:
        _, _, current_node = heapq.heappop(frontier)
        if maze.goal_test(current_node.state):
            path = reconstruct_path(current_node)
            return (path, current_node.path_cost, max_memory, nodes_expanded, True)
        nodes_expanded += 1
        for action in maze.actions(current_node.state):
            next_state = maze.result(current_node.state, action)
            cost = maze.step_cost(current_node.state, action, next_state)
            tentative_g = current_node.path_cost + cost
            if next_state not in g_scores or tentative_g < g_scores[next_state]:
                h_next = heuristic_fn(next_state, goal)
                new_node = Node(next_state, current_node, action, tentative_g, h_next)
                g_scores[next_state] = tentative_g
                heapq.heappush(frontier, (new_node.f_score, counter, new_node))
                counter += 1
                max_memory = max(max_memory, len(frontier) + len(g_scores))
    return ([], 0.0, max_memory, nodes_expanded, False)
