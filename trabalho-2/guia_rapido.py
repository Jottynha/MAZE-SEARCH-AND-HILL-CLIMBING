#!/usr/bin/env python3
"""
GUIA RÁPIDO - Trabalho 2: Hill Climbing para 8 Rainhas

Este arquivo contém comandos prontos para executar todos os experimentos.
"""

import os
import subprocess

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def main():
    print_header("GUIA RÁPIDO - TRABALHO 2: HILL CLIMBING")
    
    print("Este guia contém todos os comandos necessários para o trabalho.\n")
    
    # Menu
    print("Escolha uma opção:\n")
    print("1. Teste Rápido (10 trials, ~1 min)")
    print("2. Experimento Médio (50 trials, ~5 min)")
    print("3. Experimento Completo - TRABALHO OFICIAL (200 trials, ~30 min)")
    print("4. Comparação de Estratégias - Teste (30 trials, ~10 min)")
    print("5. Comparação de Estratégias - TRABALHO OFICIAL (200 trials, ~40 min)")
    print("6. Experimento Variando Restarts (10, 50, 100, 200)")
    print("7. Mostrar estrutura de arquivos gerados")
    print("8. Abrir documentação")
    print("0. Sair")
    
    choice = input("\nOpção: ").strip()
    
    if choice == "1":
        print_header("TESTE RÁPIDO (10 trials)")
        cmd = "python3 hill_climbing.py --trials 10 --restarts 20 --iters 500 --sideways 50 --seed 42 --no-display"
        print(f"Comando: {cmd}\n")
        subprocess.run(cmd, shell=True)
        
    elif choice == "2":
        print_header("EXPERIMENTO MÉDIO (50 trials)")
        cmd = "python3 hill_climbing.py --trials 50 --restarts 30 --iters 1000 --sideways 100 --seed 42 --no-display"
        print(f"Comando: {cmd}\n")
        subprocess.run(cmd, shell=True)
        
    elif choice == "3":
        print_header("EXPERIMENTO COMPLETO - TRABALHO OFICIAL (200 trials)")
        print("⚠️  Este experimento pode levar ~30 minutos para completar.\n")
        confirm = input("Deseja continuar? (s/n): ").strip().lower()
        if confirm == 's':
            cmd = "python3 hill_climbing.py --trials 200 --restarts 50 --iters 1000 --sideways 100 --seed 0 --no-display"
            print(f"\nComando: {cmd}\n")
            subprocess.run(cmd, shell=True)
        else:
            print("Cancelado.")
            
    elif choice == "4":
        print_header("COMPARAÇÃO DE ESTRATÉGIAS - TESTE (30 trials)")
        cmd = "python3 compare_strategies.py --trials 30 --restarts 20 --iters 500 --sideways 50 --seed 42"
        print(f"Comando: {cmd}\n")
        subprocess.run(cmd, shell=True)
        
    elif choice == "5":
        print_header("COMPARAÇÃO DE ESTRATÉGIAS - TRABALHO OFICIAL (200 trials)")
        print("⚠️  Este experimento pode levar ~40 minutos para completar.\n")
        confirm = input("Deseja continuar? (s/n): ").strip().lower()
        if confirm == 's':
            cmd = "python3 compare_strategies.py --trials 200 --restarts 50 --iters 1000 --sideways 100 --seed 0"
            print(f"\nComando: {cmd}\n")
            subprocess.run(cmd, shell=True)
        else:
            print("Cancelado.")
            
    elif choice == "6":
        print_header("EXPERIMENTO VARIANDO RESTARTS")
        cmd = "python3 hill_climbing.py --vary-restarts 10 50 100 200 --trials 30 --iters 1000 --sideways 100 --seed 42 --no-display"
        print(f"Comando: {cmd}\n")
        subprocess.run(cmd, shell=True)
        
    elif choice == "7":
        print_header("ESTRUTURA DE ARQUIVOS GERADOS")
        print("""
output/                              # Resultados do hill_climbing.py
├── csv/
│   ├── results_summary.csv          # ⭐ Dados detalhados (run_id, seed_used, solution)
│   ├── statistics_summary.csv       # ⭐ Estatísticas agregadas
│   └── summary_restarts_*.csv       # Estatísticas por valor de restart
├── boxplot/
│   └── box_times.png
├── histogram/
│   └── hist_iters.png
├── plots/
│   └── success_vs_restarts.png
└── solutions/
    └── solution_trial_*.png

output_comparison/                   # Resultados do compare_strategies.py
├── csv/
│   ├── results_best-improvement.csv
│   ├── results_first-improvement.csv
│   ├── results_best-sideways.csv
│   ├── results_best-random-restart.csv
│   └── comparison_summary.csv       # ⭐ Resumo comparativo
└── plots/
    ├── comparison_success_rate.png
    ├── comparison_time.png
    ├── comparison_iterations.png
    └── comparison_all_metrics.png   # ⭐ Gráfico principal
        """)
        
    elif choice == "8":
        print_header("DOCUMENTAÇÃO DISPONÍVEL")
        print("""
Arquivos de documentação no diretório trabalho-2/:

1. README.md
   - Guia principal de uso
   - Instruções de instalação e execução
   - Explicação de parâmetros
   - Como reproduzir resultados

2. MELHORIAS.md
   - Detalhamento técnico das melhorias
   - Comparação antes/depois do código
   - Justificativas teóricas

3. COMPARACAO_ESTRATEGIAS.md
   - Explicação de cada estratégia
   - Pseudocódigo detalhado
   - Análise de trade-offs
   - Guia para relatório

4. RESUMO_IMPLEMENTACAO.md
   - Resumo executivo de tudo implementado
   - Checklist completo
   - Comandos principais

5. exemplo_uso.py
   - Demonstração prática
   - Exemplos de análise com pandas

Para abrir um arquivo:
  cat README.md
  less COMPARACAO_ESTRATEGIAS.md
        """)
        
    elif choice == "0":
        print("Saindo...")
        return
        
    else:
        print("❌ Opção inválida!")
        return
    
    # Após execução, mostrar próximos passos
    if choice in ["1", "2", "3", "4", "5", "6"]:
        print_header("EXECUÇÃO CONCLUÍDA")
        print("Próximos passos:\n")
        
        if choice in ["1", "2", "3", "6"]:
            print("1. Ver resumo estatístico:")
            print("   cat output/csv/statistics_summary.csv\n")
            print("2. Ver dados detalhados:")
            print("   head -20 output/csv/results_summary.csv\n")
            print("3. Visualizar gráficos:")
            print("   xdg-open output/boxplot/box_times.png")
            print("   xdg-open output/histogram/hist_iters.png\n")
            
        elif choice in ["4", "5"]:
            print("1. Ver resumo comparativo:")
            print("   cat output_comparison/csv/comparison_summary.csv\n")
            print("2. Visualizar gráfico principal:")
            print("   xdg-open output_comparison/plots/comparison_all_metrics.png\n")
            print("3. Ver dados por estratégia:")
            print("   head -20 output_comparison/csv/results_best-improvement.csv\n")
        
        print("4. Analisar com Python/Pandas:")
        print("   python3 exemplo_uso.py\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
