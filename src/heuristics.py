from typing import Tuple
import math

Pos = Tuple[int, int]  # (linha, coluna)

def h_manhattan(a: Pos, b: Pos) -> float:
    """
    Distância Manhattan entre a e b.
    (Admissível em grade de 4-direções).
    """
    r1, c1 = a
    r2, c2 = b
    return float(abs(r1 - r2) + abs(c1 - c2))

def h_euclidiana(a: Pos, b: Pos) -> float:
    """
    Distância Euclidiana entre a e b.
    (Pode ser usada conforme o modelo do problema).
    """
    r1, c1 = a
    r2, c2 = b
    # Calcula a distância euclidiana (raiz((x2-x1)^2 + (y2-y1)^2))
    return math.sqrt((r1 - r2)**2 + (c1 - c2)**2)

# Adicionei essas heuristícas, adicionar mais caso necessário (acho que só essas duas dá).