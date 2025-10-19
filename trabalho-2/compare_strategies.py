#!/usr/bin/env python3
"""
compare_strategies.py

Compara diferentes estratégias de Hill Climbing:
1. Best-improvement (steepest ascent) - escolhe o melhor vizinho
2. First-improvement - escolhe o primeiro vizinho que melhora
3. Random-restart - best-improvement com reinícios
4. Movimentos laterais controlados - permite platôs

Uso:
    python3 compare_strategies.py --trials 100 --restarts 50 --seed 42
"""

from typing import List, Dict, Any, Optional
import random
import time
import csv
import argparse
import statistics
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd

from eight_queens import random_board, conflicts

Board = List[int]


class HillClimberBase:
    """Classe base para Hill Climbing com diferentes estratégias"""
    
    def __init__(self, n: int = 8, max_iters: int = 1000, strategy: str = 'best'):
        self.n = n
        self.max_iters = max_iters
        self.strategy = strategy  # 'best', 'first', 'sideways'
        
    def neighbors(self, board: Board):
        """Gera vizinhos através de swap de colunas (permutações)."""
        n = self.n
        for i in range(n - 1):
            for j in range(i + 1, n):
                nb = board.copy()
                nb[i], nb[j] = nb[j], nb[i]
                yield nb, (i, j)
    
    def climb(self, start: Board) -> Dict[str, Any]:
        """Executa hill climbing - método abstrato sobrescrito nas subclasses"""
        raise NotImplementedError


class BestImprovementClimber(HillClimberBase):
    """Best-improvement (steepest ascent): avalia todos os vizinhos e escolhe o melhor"""
    
    def __init__(self, n: int = 8, max_iters: int = 1000):
        super().__init__(n, max_iters, strategy='best')
    
    def climb(self, start: Board) -> Dict[str, Any]:
        current = start.copy()
        current_val = conflicts(current)
        
        result = {
            "start": start,
            "final": current,
            "start_conflicts": current_val,
            "final_conflicts": current_val,
            "iters": 0,
            "success": current_val == 0,
            "strategy": "best-improvement"
        }
        
        if current_val == 0:
            return result
        
        for it in range(1, self.max_iters + 1):
            # Avalia TODOS os vizinhos para encontrar o melhor
            best_neighbor = None
            best_val = current_val
            
            for nb, mv in self.neighbors(current):
                val = conflicts(nb)
                if val < best_val:
                    best_val = val
                    best_neighbor = nb
            
            # Se não encontrou vizinho melhor, para (mínimo local)
            if best_neighbor is None:
                result.update({
                    "final": current,
                    "final_conflicts": current_val,
                    "iters": it,
                    "success": False
                })
                return result
            
            # Move para o melhor vizinho
            current = best_neighbor
            current_val = best_val
            
            # Verifica se encontrou solução
            if current_val == 0:
                result.update({
                    "final": current,
                    "final_conflicts": 0,
                    "iters": it,
                    "success": True
                })
                return result
        
        # Esgotou iterações
        result.update({
            "final": current,
            "final_conflicts": current_val,
            "iters": self.max_iters,
            "success": current_val == 0
        })
        return result


class FirstImprovementClimber(HillClimberBase):
    """First-improvement: escolhe o primeiro vizinho que melhora"""
    
    def __init__(self, n: int = 8, max_iters: int = 1000):
        super().__init__(n, max_iters, strategy='first')
    
    def climb(self, start: Board) -> Dict[str, Any]:
        current = start.copy()
        current_val = conflicts(current)
        
        result = {
            "start": start,
            "final": current,
            "start_conflicts": current_val,
            "final_conflicts": current_val,
            "iters": 0,
            "success": current_val == 0,
            "strategy": "first-improvement"
        }
        
        if current_val == 0:
            return result
        
        for it in range(1, self.max_iters + 1):
            # Procura o PRIMEIRO vizinho que melhora
            found_improvement = False
            
            for nb, mv in self.neighbors(current):
                val = conflicts(nb)
                if val < current_val:
                    # Encontrou melhoria - aceita imediatamente
                    current = nb
                    current_val = val
                    found_improvement = True
                    break  # Não avalia outros vizinhos
            
            # Se não encontrou melhoria, para (mínimo local)
            if not found_improvement:
                result.update({
                    "final": current,
                    "final_conflicts": current_val,
                    "iters": it,
                    "success": False
                })
                return result
            
            # Verifica se encontrou solução
            if current_val == 0:
                result.update({
                    "final": current,
                    "final_conflicts": 0,
                    "iters": it,
                    "success": True
                })
                return result
        
        # Esgotou iterações
        result.update({
            "final": current,
            "final_conflicts": current_val,
            "iters": self.max_iters,
            "success": current_val == 0
        })
        return result


class SidewaysClimber(HillClimberBase):
    """Best-improvement com movimentos laterais (permite platôs)"""
    
    def __init__(self, n: int = 8, max_iters: int = 1000, max_sideways: int = 100):
        super().__init__(n, max_iters, strategy='sideways')
        self.max_sideways = max_sideways
    
    def climb(self, start: Board) -> Dict[str, Any]:
        current = start.copy()
        current_val = conflicts(current)
        
        result = {
            "start": start,
            "final": current,
            "start_conflicts": current_val,
            "final_conflicts": current_val,
            "iters": 0,
            "success": current_val == 0,
            "used_sideways": 0,
            "strategy": "sideways-moves"
        }
        
        if current_val == 0:
            return result
        
        sideways_used = 0
        
        for it in range(1, self.max_iters + 1):
            # Avalia todos os vizinhos
            best_neighbor = None
            best_val = float('inf')
            
            for nb, mv in self.neighbors(current):
                val = conflicts(nb)
                if val < best_val:
                    best_val = val
                    best_neighbor = nb
            
            # Verifica se melhora ou se é movimento lateral permitido
            if best_val < current_val:
                # Melhoria real
                current = best_neighbor
                current_val = best_val
                sideways_used = 0
            elif best_val == current_val and sideways_used < self.max_sideways:
                # Movimento lateral (platô)
                current = best_neighbor
                current_val = best_val
                sideways_used += 1
            else:
                # Não pode mais melhorar ou fazer movimentos laterais
                result.update({
                    "final": current,
                    "final_conflicts": current_val,
                    "iters": it,
                    "success": False,
                    "used_sideways": sideways_used
                })
                return result
            
            # Verifica se encontrou solução
            if current_val == 0:
                result.update({
                    "final": current,
                    "final_conflicts": 0,
                    "iters": it,
                    "success": True,
                    "used_sideways": sideways_used
                })
                return result
        
        # Esgotou iterações
        result.update({
            "final": current,
            "final_conflicts": current_val,
            "iters": self.max_iters,
            "success": current_val == 0,
            "used_sideways": sideways_used
        })
        return result


class RandomRestartClimber:
    """Random-restart: reinicia com configuração aleatória quando preso"""
    
    def __init__(self, base_climber: HillClimberBase, max_restarts: int = 100):
        self.base_climber = base_climber
        self.max_restarts = max_restarts
    
    def run(self) -> Dict[str, Any]:
        start_time = time.perf_counter()
        total_iters = 0
        best = None
        best_conf = None
        
        for restart in range(self.max_restarts):
            start_board = random_board(self.base_climber.n)
            res = self.base_climber.climb(start_board)
            total_iters += res["iters"]
            
            if best is None or res["final_conflicts"] < best_conf:
                best = res["final"]
                best_conf = res["final_conflicts"]
            
            if res["success"]:
                elapsed = time.perf_counter() - start_time
                return {
                    "success": True,
                    "solution": res["final"],
                    "final_conflicts": 0,
                    "restarts_used": restart + 1,
                    "total_iterations": total_iters,
                    "time_s": elapsed,
                    "strategy": f"{res['strategy']}-random-restart"
                }
        
        elapsed = time.perf_counter() - start_time
        return {
            "success": False,
            "solution": best,
            "final_conflicts": best_conf,
            "restarts_used": self.max_restarts,
            "total_iterations": total_iters,
            "time_s": elapsed,
            "strategy": f"{self.base_climber.strategy}-random-restart"
        }


def run_comparison(trials: int, restarts: int, max_iters: int, max_sideways: int, seed: int):
    """Executa comparação entre as 4 estratégias"""
    
    strategies = {
        'best-improvement': BestImprovementClimber(max_iters=max_iters),
        'first-improvement': FirstImprovementClimber(max_iters=max_iters),
        'best-sideways': SidewaysClimber(max_iters=max_iters, max_sideways=max_sideways),
        'best-random-restart': BestImprovementClimber(max_iters=max_iters)
    }
    
    all_results = {}
    
    for strategy_name, climber in strategies.items():
        print(f"\n{'='*60}")
        print(f"Executando: {strategy_name}")
        print(f"{'='*60}")
        
        results = []
        base_seed = seed
        
        for t in range(trials):
            seed_for_run = base_seed + t
            random.seed(seed_for_run)
            np.random.seed(seed_for_run)
            
            start_board = random_board(8)
            
            # Para random-restart, usa o wrapper
            if 'random-restart' in strategy_name:
                runner = RandomRestartClimber(climber, max_restarts=restarts)
                r = runner.run()
            else:
                # Sem random-restart
                start_time = time.perf_counter()
                r = climber.climb(start_board)
                r['time_s'] = time.perf_counter() - start_time
                r['restarts_used'] = 1  # Sem reinícios
                r['total_iterations'] = r['iters']
                r['solution'] = r['final']
            
            r['run_id'] = t + 1
            r['seed_used'] = seed_for_run
            r['strategy'] = strategy_name
            results.append(r)
            
            if (t + 1) % 10 == 0:
                print(f"  Progresso: {t+1}/{trials} trials concluídas")
        
        all_results[strategy_name] = results
        
        # Estatísticas rápidas
        success_rate = sum(1 for r in results if r['success']) / len(results)
        mean_time = statistics.mean(r['time_s'] for r in results)
        print(f"\n  ✓ Taxa de sucesso: {success_rate*100:.1f}%")
        print(f"  ✓ Tempo médio: {mean_time:.4f}s")
    
    return all_results


def save_comparison_results(all_results: Dict[str, List[Dict]], output_dir: str):
    """Salva resultados da comparação em CSVs e gera gráficos"""
    
    # Criar diretórios
    csv_dir = os.path.join(output_dir, "csv")
    plots_dir = os.path.join(output_dir, "plots")
    os.makedirs(csv_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)
    
    # 1. CSV detalhado por estratégia
    for strategy, results in all_results.items():
        filename = os.path.join(csv_dir, f'results_{strategy}.csv')
        with open(filename, 'w', newline='') as f:
            fieldnames = ['run_id', 'seed_used', 'success', 'restarts_used', 
                         'total_iterations', 'time_s', 'final_conflicts', 'strategy']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow({k: r.get(k) for k in fieldnames})
    
    # 2. CSV de comparação agregada
    comparison_data = []
    for strategy, results in all_results.items():
        times = [r['time_s'] for r in results]
        iters = [r['total_iterations'] for r in results]
        restarts = [r['restarts_used'] for r in results]
        final_conf = [r['final_conflicts'] for r in results]
        success_rate = sum(1 for r in results if r['success']) / len(results)
        
        comparison_data.append({
            'strategy': strategy,
            'success_rate': success_rate,
            'mean_time': statistics.mean(times),
            'std_time': statistics.pstdev(times) if len(times) > 1 else 0,
            'mean_iters': statistics.mean(iters),
            'std_iters': statistics.pstdev(iters) if len(iters) > 1 else 0,
            'mean_restarts': statistics.mean(restarts),
            'mean_final_conflicts': statistics.mean(final_conf),
        })
    
    df_comparison = pd.DataFrame(comparison_data)
    df_comparison.to_csv(os.path.join(csv_dir, 'comparison_summary.csv'), index=False)
    
    print("\n" + "="*60)
    print("RESUMO DA COMPARAÇÃO")
    print("="*60)
    print(df_comparison.to_string(index=False))
    
    # 3. Gráficos comparativos
    plot_comparison_metrics(df_comparison, plots_dir)
    
    return df_comparison


def plot_comparison_metrics(df: pd.DataFrame, output_dir: str):
    """Gera gráficos comparativos entre as estratégias"""
    
    strategies = df['strategy'].values
    
    # 1. Taxa de sucesso
    plt.figure(figsize=(10, 6))
    plt.bar(strategies, df['success_rate'] * 100, color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'])
    plt.ylabel('Taxa de Sucesso (%)', fontsize=12)
    plt.title('Comparação: Taxa de Sucesso por Estratégia', fontsize=14, fontweight='bold')
    plt.xticks(rotation=15, ha='right')
    plt.ylim(0, 105)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'comparison_success_rate.png'), dpi=200)
    plt.close()
    
    # 2. Tempo médio
    plt.figure(figsize=(10, 6))
    plt.bar(strategies, df['mean_time'], yerr=df['std_time'], 
            color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'], capsize=5)
    plt.ylabel('Tempo Médio (s)', fontsize=12)
    plt.title('Comparação: Tempo de Execução por Estratégia', fontsize=14, fontweight='bold')
    plt.xticks(rotation=15, ha='right')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'comparison_time.png'), dpi=200)
    plt.close()
    
    # 3. Iterações médias
    plt.figure(figsize=(10, 6))
    plt.bar(strategies, df['mean_iters'], yerr=df['std_iters'],
            color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'], capsize=5)
    plt.ylabel('Iterações Médias', fontsize=12)
    plt.title('Comparação: Número de Iterações por Estratégia', fontsize=14, fontweight='bold')
    plt.xticks(rotation=15, ha='right')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'comparison_iterations.png'), dpi=200)
    plt.close()
    
    # 4. Gráfico combinado (múltiplas métricas)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Taxa de sucesso
    axes[0, 0].bar(strategies, df['success_rate'] * 100, color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'])
    axes[0, 0].set_ylabel('Taxa de Sucesso (%)')
    axes[0, 0].set_title('Taxa de Sucesso')
    axes[0, 0].tick_params(axis='x', rotation=15)
    axes[0, 0].grid(axis='y', alpha=0.3)
    
    # Tempo
    axes[0, 1].bar(strategies, df['mean_time'], color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'])
    axes[0, 1].set_ylabel('Tempo (s)')
    axes[0, 1].set_title('Tempo Médio')
    axes[0, 1].tick_params(axis='x', rotation=15)
    axes[0, 1].grid(axis='y', alpha=0.3)
    
    # Iterações
    axes[1, 0].bar(strategies, df['mean_iters'], color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'])
    axes[1, 0].set_ylabel('Iterações')
    axes[1, 0].set_title('Iterações Médias')
    axes[1, 0].tick_params(axis='x', rotation=15)
    axes[1, 0].grid(axis='y', alpha=0.3)
    
    # Conflitos finais
    axes[1, 1].bar(strategies, df['mean_final_conflicts'], color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'])
    axes[1, 1].set_ylabel('Conflitos')
    axes[1, 1].set_title('Conflitos Finais Médios')
    axes[1, 1].tick_params(axis='x', rotation=15)
    axes[1, 1].grid(axis='y', alpha=0.3)
    
    plt.suptitle('Comparação de Estratégias de Hill Climbing', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'comparison_all_metrics.png'), dpi=200)
    plt.close()
    
    print(f"\n✓ Gráficos salvos em {output_dir}/")


def main():
    parser = argparse.ArgumentParser(description='Compara estratégias de Hill Climbing')
    parser.add_argument('--trials', type=int, default=100, help='Número de execuções por estratégia')
    parser.add_argument('--restarts', type=int, default=50, help='Número máximo de reinícios (para random-restart)')
    parser.add_argument('--iters', type=int, default=1000, help='Iterações máximas por subida')
    parser.add_argument('--sideways', type=int, default=100, help='Movimentos laterais máximos')
    parser.add_argument('--seed', type=int, default=42, help='Semente para reprodutibilidade')
    parser.add_argument('--output', type=str, default='output_comparison', help='Diretório de saída')
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("COMPARAÇÃO DE ESTRATÉGIAS DE HILL CLIMBING")
    print("="*60)
    print(f"\nParâmetros:")
    print(f"  - Trials por estratégia: {args.trials}")
    print(f"  - Max restarts (random-restart): {args.restarts}")
    print(f"  - Max iterações: {args.iters}")
    print(f"  - Max movimentos laterais: {args.sideways}")
    print(f"  - Seed: {args.seed}")
    
    print("\nEstratégias comparadas:")
    print("  1. Best-improvement (steepest ascent)")
    print("  2. First-improvement")
    print("  3. Best-improvement + Sideways moves")
    print("  4. Best-improvement + Random restart")
    
    # Executar comparação
    all_results = run_comparison(
        trials=args.trials,
        restarts=args.restarts,
        max_iters=args.iters,
        max_sideways=args.sideways,
        seed=args.seed
    )
    
    # Salvar resultados
    save_comparison_results(all_results, args.output)
    
    print("\n" + "="*60)
    print("✅ COMPARAÇÃO CONCLUÍDA")
    print("="*60)
    print(f"\nResultados salvos em: {args.output}/")
    print(f"  - CSVs detalhados: {args.output}/csv/")
    print(f"  - Gráficos: {args.output}/plots/")


if __name__ == '__main__':
    main()
