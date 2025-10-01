# Implementações sugeridas (em grande parte) pelo Thiago.
from typing import List, Tuple, Dict

Grid = List[List[str]]
Pos = Tuple[int, int]  # (linha, coluna)

class Maze:
    """
    Representa o espaço de estados para o problema do labirinto.
    Convenções:
    - 'S' = inı́cio, 'G' = objetivo, '#' = parede, '.' = célula livre.
    - Ações: mover para N, S, O, L (4-direções), se necessário expandimos para 8.
    """
    def __init__(self, grid: Grid):
        self.grid = grid
        self.H = len(grid)
        self.W = len(grid[0]) if self.H > 0 else 0
        self.start = self._find('S')
        self.goal = self._find('G')

    def from_file(filepath: str) -> 'Maze':
        """Carrega o labirinto de um arquivo de texto."""
        grid: Grid = []
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    # Remove quebras de linha e converte para lista de caracteres
                    grid.append(list(line.strip()))
            return Maze(grid)
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo '{filepath}' não encontrado.")

    def _find(self, ch: str) -> Pos:
        """Encontra a posição (linha, coluna) de um caractere."""
        for r in range(self.H):
            for c in range(self.W):
                if self.grid[r][c] == ch:
                    return (r, c)
        raise ValueError(f"Caractere '{ch}' não encontrado no grid")

    def in_bounds(self, p: Pos) -> bool:
        """Verifica se a posição está dentro dos limites do grid."""
        r, c = p
        return 0 <= r < self.H and 0 <= c < self.W

    def passable(self, p: Pos) -> bool:
        """Verifica se a posição não é uma parede ('#')."""
        r, c = p
        return self.grid[r][c] != '#'

    def actions(self, p: Pos) -> List[str]:
        """Retorna a lista de ações válidas (N, S, O, L) em p."""
        r, c = p
        acts: List[str] = []
        # Candidatos: 'Ação': (nova_linha, nova_coluna)
        candidates: Dict[str, Pos] = {
            'N': (r - 1, c),
            'S': (r + 1, c),
            'O': (r, c - 1),
            'L': (r, c + 1),
        }

        for a, q in candidates.items():
            # Transição: aplicar a ação e validar limites/obstáculos [cite: 45]
            if self.in_bounds(q) and self.passable(q):
                acts.append(a)
        return acts

    def result(self, p: Pos, a: str) -> Pos:
        """Função de transição: retorna a nova posição q após aplicar a ação a em p."""
        r, c = p
        delta: Dict[str, Tuple[int, int]] = {'N': (-1, 0), 'S': (1, 0), 'O': (0, -1), 'L': (0, 1)}
        
        if a not in delta:
            raise ValueError(f"Ação desconhecida: {a}")
            
        dr, dc = delta[a]
        q = (r + dr, c + dc)

        if not (self.in_bounds(q) and self.passable(q)):
            raise ValueError("Ação inválida ou leva a um obstáculo/limite.")
            
        return q

    def step_cost(self, p: Pos, a: str, q: Pos) -> float:
        """Custo de passo. Por padrão, custo unitário (1.0)."""
        return 1.0  # Custo unitário por passo

    def goal_test(self, p: Pos) -> bool:
        """Teste de objetivo: verifica se a posição p é a meta."""
        return p == self.goal  # Posição 

if __name__ == '__main__':
    # Exemplo de uso (testando a classe Maze)
    try:
        # Usando o arquivo 'data/labirinto.txt' como exemplo acima para rodar
        mz = Maze.from_file('data/labirinto.txt') 
        s = mz.start
        print(f"Início (S): {s}")
        print(f"Objetivo (G): {mz.goal}")
        print(f"Ações válidas em S: {mz.actions(s)}")
    except (FileNotFoundError, ValueError) as e:
        print(f"Erro ao carregar o labirinto: {e}")