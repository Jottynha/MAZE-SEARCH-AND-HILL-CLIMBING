"""
eight_queens.py

Representação do tabuleiro 8-rainhas e utilitários.
"""
from typing import List
import random

Board = List[int]


def random_board(n: int = 8) -> Board:
    """Gera um tabuleiro aleatório (vetor: índice=coluna, valor=linha)."""
    return [random.randrange(n) for _ in range(n)]


def conflicts(board: Board) -> int:
    """Conta pares de rainhas que se atacam."""
    n = len(board)
    c = 0
    for i in range(n):
        for j in range(i + 1, n):
            if board[i] == board[j] or abs(board[i] - board[j]) == abs(i - j):
                c += 1
    return c


def board_matrix(board: Board) -> List[List[int]]:
    n = len(board)
    mat = [[0 for _ in range(n)] for _ in range(n)]
    for col, row in enumerate(board):
        mat[row][col] = 1
    return mat


def pretty_print(board: Board) -> None:
    n = len(board)
    for r in range(n):
        row = ""
        for c in range(n):
            row += "Q " if board[c] == r else ". "
        print(row)
    print(f"Conflicts: {conflicts(board)}")
    print("Board vector (col->row):", board)


if __name__ == "__main__":
    b = random_board(8)
    pretty_print(b)
