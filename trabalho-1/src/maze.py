"""
maze.py
-> Lê ficheiro com posições e bitstrings (N,S,L,O)
-> Cria um objeto da Classe Maze onde cada posição tem a sua lista de adjacência. 
-> Executa BFS do Start ao Goal.
Formato adotado que será aceito por linha:
-> [r,c]:1001   (ou)  
-> r,c:1001
Comentários com '#' são ignorados; se houver "# A" no final a posição ganha rótulo 'A'.
Linhas especiais:
-> Start:[r,c] (Estado inicial do agente)
-> Goal:[r,c] (Estado meta do agente)
Por padrão lê 'data/labirinto.txt' se nenhum ficheiro for passado como argumento.
"""

from typing import Dict, Tuple, List, Optional
from collections import deque
import re
import sys
import argparse

Pos = Tuple[int,int]
ORDER = ['N','S','L','O']  # ordem dos bits da lisat de adjacência

class Maze:
    DELTA = {'N':(-1,0),'S':(1,0),'L':(0,1),'O':(0,-1)}
    def __init__(self, adj_map: Dict[Pos,str], pos_label: Optional[Dict[Pos,str]] = None):
        """
        adj_map: mapa Pos -> bits (string len==4 com '0'/'1' na ordem [N,S,L,O])
        pos_label: opcional mapa Pos -> label (ex. 'A')
        """
        self.adj_map = adj_map
        self.pos_label = pos_label or {}
        # infere limites (não necessário mas útil)
        rows = [p[0] for p in adj_map.keys()] if adj_map else [0]
        cols = [p[1] for p in adj_map.keys()] if adj_map else [0]
        self.H = max(rows)+1
        self.W = max(cols)+1

    @classmethod
    def from_file(cls, path: str) -> Tuple['Maze', Optional[Pos], Optional[Pos]]:
        """
        Lê o arquivo e devolve (MazeAdj, start_pos, goal_pos)
        """
        adj_map: Dict[Pos,str] = {}
        pos_label: Dict[Pos,str] = {}
        start_pos: Optional[Pos] = None
        goal_pos: Optional[Pos] = None

        line_pat = re.compile(r'\[?\s*(\d+)\s*,\s*(\d+)\s*\]?\s*:\s*([01]{4})')
        special_pat = re.compile(r'^(Start|Goal)\s*:\s*\[?\s*(\d+)\s*,\s*(\d+)\s*\]?', re.IGNORECASE)

        try:
            with open(path, 'r', encoding='utf-8') as f:
                for raw in f:
                    # preserva comentário separado para poder extrair label se houver
                    raw_line = raw.rstrip('\n')
                    line = raw_line.split('#',1)[0].strip()  # parte antes do comentário
                    # procura special Start/Goal (podem ter comentário depois com label)
                    msp = special_pat.match(line)
                    if msp:
                        key = msp.group(1).lower()
                        r = int(msp.group(2)); c = int(msp.group(3))
                        if key == 'start':
                            start_pos = (r,c)
                        else:
                            goal_pos = (r,c)
                        # tenta extrair label do comentário (após '#')
                        if '#' in raw_line:
                            com = raw_line.split('#',1)[1].strip()
                            if com:
                                pos_label[(r,c)] = com.split()[0]
                        continue

                    m = line_pat.search(line)
                    if not m:
                        continue
                    r = int(m.group(1)); c = int(m.group(2))
                    bits = m.group(3)
                    adj_map[(r,c)] = bits
                    # se houver comentário com label (exemplo "# A"), associar
                    if '#' in raw_line:
                        lab = raw_line.split('#',1)[1].strip()
                        if lab:
                            pos_label[(r,c)] = lab.split()[0]
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo '{path}' não encontrado.")

        maze = cls(adj_map, pos_label)
        return maze, start_pos, goal_pos

    def passable(self, p: Pos) -> bool:
        return p in self.adj_map

    def in_bounds(self, p: Pos) -> bool:
        # posição em adj_map é suficiente
        return p in self.adj_map

    def actions(self, p: Pos) -> List[str]:
        """
        Retorna ações possíveis (N,S,L,O) a partir de p, avaliando bits da lista 
        e existência do vizinho.
        """
        if p not in self.adj_map:
            return []
        bits = self.adj_map[p]
        acts: List[str] = []
        for i, ch in enumerate(bits):
            if ch == '0':  # 0 = pode andar
                a = ORDER[i]
                dr,dc = self.DELTA[a]
                q = (p[0]+dr, p[1]+dc)
                # só considera ação se o destino existir (passable)
                if self.in_bounds(q):
                    acts.append(a)
        return acts

    def result(self, p: Pos, a: str) -> Pos:
        if a not in self.DELTA:
            raise ValueError(f"Ação inválida: {a}")
        if p not in self.adj_map:
            raise ValueError(f"Posição {p} não é transitável/no mapa.")
        bits = self.adj_map[p]
        idx = ORDER.index(a)
        if bits[idx] != '0':
            raise ValueError(f"Ação {a} bloqueada em {p} (bit=1).")
        dr,dc = self.DELTA[a]
        q = (p[0]+dr, p[1]+dc)
        if not self.in_bounds(q):
            raise ValueError(f"Ação {a} leva a posição fora do mapa: {q}.")
        return q

    def pretty_print(self):
        print(f"MazeAdj: tamanho aproximado H={self.H} W={self.W}, células={len(self.adj_map)}")
        for p in sorted(self.adj_map.keys()):
            label = self.pos_label.get(p, '')
            bits = self.adj_map[p]
            acts = self.actions(p)
            lab_str = f" #{label}" if label else ""
            print(f"  {p}{lab_str}: {bits} -> ações: {acts}")

    def bfs(self, start: Pos, goal: Pos) -> Optional[List[Pos]]:
        if start not in self.adj_map or goal not in self.adj_map:
            return None
        q = deque([start])
        parent: Dict[Pos, Optional[Pos]] = {start: None}
        while q:
            cur = q.popleft()
            if cur == goal:
                # reconstrói caminho
                path = []
                node = cur
                while node is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()
                return path
            for a in self.actions(cur):
                nxt = self.result(cur, a)
                if nxt not in parent:
                    parent[nxt] = cur
                    q.append(nxt)
        return None

# Main para testes
def main():
    parser = argparse.ArgumentParser(description="Lê adjacências por posição (bits) e faz BFS.")
    parser.add_argument('file', nargs='?', default='data/labirinto.txt',
                        help="ficheiro com adjacências por posição (default: data/labirinto.txt)")
    parser.add_argument('--start', help='start override: r,c', default=None)
    parser.add_argument('--goal', help='goal override: r,c', default=None)
    args = parser.parse_args()

    try:
        maze, fstart, fgoal = Maze.from_file(args.file)
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)
    # parse para overrides se dados em --start/--goal
    def parse_rc(s: Optional[str]) -> Optional[Pos]:
        if not s: return None
        s = s.strip()
        m = re.match(r'\[?\s*(\d+)\s*,\s*(\d+)\s*\]?', s)
        if not m: return None
        return (int(m.group(1)), int(m.group(2)))

    start = parse_rc(args.start) or fstart
    goal = parse_rc(args.goal) or fgoal

    print("== Labirinto carregado ==")
    maze.pretty_print()
    if start is None or goal is None:
        print("\nStart ou Goal não especificados — especifica Start e Goal para procurar caminho.")
        print(f"Start (encontrado no ficheiro) = {fstart}, Goal = {fgoal}")
        sys.exit(0)

    print(f"\nProcurando caminho BFS de {start} -> {goal} ...")
    path = maze.bfs(start, goal)
    if path is None:
        print("Nenhum caminho encontrado (start/goal inválidos ou desconectados).")
        sys.exit(0)
    print("Caminho (coords):", " -> ".join(str(p) for p in path))
    # se houver rótulos, mostra também
    if maze.pos_label:
        print("Caminho (labels):", " -> ".join(maze.pos_label.get(p, '?') for p in path))

if __name__ == '__main__':
    main()
