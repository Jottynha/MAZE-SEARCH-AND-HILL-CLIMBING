#!/usr/bin/env python3
"""
GUIA RÁPIDO - Trabalho 2: Hill Climbing para 8 Rainhas

Script principal para executar os experimentos do relatório.
Implementa Hill Climbing com Random Restart e Sideways Moves.
"""

import os
import subprocess

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def main():
    print_header("TRABALHO 2: HILL CLIMBING PARA 8 RAINHAS")
    
    print("Experimentos disponíveis:\n")
    
    # Menu simplificado
    print("1. Teste Rápido (10 trials, ~30 segundos)")
    print("2. Experimento Médio (50 trials, ~3 minutos)")
    print("3. 🎯 EXPERIMENTO COMPLETO - RELATÓRIO (201 trials, ~15 minutos)")
    print("4. Experimento Variando Restarts (10, 50, 100, 200)")
    print("5. Demonstração Única Execução (com visualização)")
    print("6. Mostrar estrutura de saída")
    print("0. Sair")
    
    choice = input("\nOpção: ").strip()
    
    if choice == "1":
        print_header("TESTE RÁPIDO (10 trials)")
        cmd = "python3 hill_climbing.py --trials 10 --restarts 30 --iters 1000 --sideways 100 --seed 42 --no-display"
        print(f"Comando: {cmd}\n")
        subprocess.run(cmd, shell=True)
        
    elif choice == "2":
        print_header("EXPERIMENTO MÉDIO (50 trials)")
        cmd = "python3 hill_climbing.py --trials 50 --restarts 50 --iters 1000 --sideways 100 --seed 42 --no-display"
        print(f"Comando: {cmd}\n")
        subprocess.run(cmd, shell=True)
        
    elif choice == "3":
        print_header("🎯 EXPERIMENTO COMPLETO PARA RELATÓRIO (201 trials)")
        print("Este é o experimento principal usado no relatório.")
        print("⏱️  Tempo estimado: ~15 minutos\n")
        confirm = input("Deseja continuar? (s/n): ").strip().lower()
        if confirm == 's':
            cmd = "python3 hill_climbing.py --trials 201 --restarts 50 --iters 1000 --sideways 100 --seed 42 --no-display"
            print(f"\nComando: {cmd}\n")
            subprocess.run(cmd, shell=True)
            print("\n" + "="*70)
            print("✅ EXPERIMENTO CONCLUÍDO!")
            print("="*70)
            print("\nResultados salvos em: output/")
            print("  - CSVs: output/csv/")
            print("  - Gráficos: output/plots/ e output/histogram/")
            print("  - Soluções: output/solutions/")
        else:
            print("Cancelado.")
            
    elif choice == "4":
        print_header("EXPERIMENTO VARIANDO RESTARTS")
        print("Testa com 10, 50, 100 e 200 reinícios máximos\n")
        cmd = "python3 hill_climbing.py --vary-restarts 10 50 100 200 --trials 50 --iters 1000 --sideways 100 --seed 42 --no-display"
        print(f"Comando: {cmd}\n")
        subprocess.run(cmd, shell=True)
        
    elif choice == "5":
        print_header("DEMONSTRAÇÃO ÚNICA EXECUÇÃO")
        print("Executa uma vez e mostra visualização do tabuleiro\n")
        cmd = "python3 hill_climbing.py --trials 1 --restarts 50 --iters 1000 --sideways 100 --seed 99"
        print(f"Comando: {cmd}\n")
        subprocess.run(cmd, shell=True)
        
    elif choice == "7":
        print_header("ESTRUTURA DE ARQUIVOS GERADOS")
        
    elif choice == "6":
        print_header("ESTRUTURA DE ARQUIVOS GERADOS")
        print("""
output/                              # Resultados dos experimentos
├── csv/
│   ├── results_summary.csv          # ⭐ Dados detalhados (run_id, seed_used, solution)
│   ├── statistics_summary.csv       # ⭐ Estatísticas agregadas
│   └── results_restarts_*.csv       # Resultados por valor de restart
├── boxplot/
│   └── box_times.png                # Boxplot dos tempos de execução
├── histogram/
│   └── hist_iters.png               # Histograma das iterações
├── plots/
│   └── success_vs_restarts.png      # Taxa de sucesso vs restarts
└── solutions/
    └── solution_restarts_*_trial_*.png  # Visualização de soluções
        """)
        
    elif choice == "0":
        print("Saindo...")
        return
        
    else:
        print("❌ Opção inválida!")
        return
    
    # Após execução, mostrar próximos passos
    if choice in ["1", "2", "3", "4", "5"]:
        print_header("PRÓXIMOS PASSOS")
        print("\n📊 Visualizar resultados:\n")
        print("1. Ver resumo estatístico:")
        print("   cat output/csv/statistics_summary.csv\n")
        print("2. Ver dados detalhados (primeiras 20 linhas):")
        print("   head -20 output/csv/results_summary.csv\n")
        print("3. Abrir gráficos:")
        print("   xdg-open output/boxplot/box_times.png")
        print("   xdg-open output/histogram/hist_iters.png")
        print("   xdg-open output/plots/success_vs_restarts.png\n")
        print("4. Ver solução de exemplo:")
        print("   ls output/solutions/\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
