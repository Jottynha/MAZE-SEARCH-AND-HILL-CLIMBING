#!/bin/bash
# Script para executar a comparação de estratégias de Hill Climbing

echo "=========================================="
echo "COMPARAÇÃO DE ESTRATÉGIAS - HILL CLIMBING"
echo "=========================================="
echo ""

# Opção 1: Teste rápido (5 trials)
echo "Opção 1: Teste rápido (5 trials)"
echo "Comando: python3 compare_strategies.py --trials 5 --restarts 10 --iters 200 --sideways 30 --seed 99"
echo ""

# Opção 2: Teste médio (30 trials)
echo "Opção 2: Teste médio (30 trials) - RECOMENDADO PARA DESENVOLVIMENTO"
echo "Comando: python3 compare_strategies.py --trials 30 --restarts 20 --iters 500 --sideways 50 --seed 42"
echo ""

# Opção 3: Teste completo (100 trials)
echo "Opção 3: Teste completo (100 trials)"
echo "Comando: python3 compare_strategies.py --trials 100 --restarts 50 --iters 1000 --sideways 100 --seed 42"
echo ""

# Opção 4: Trabalho oficial (200 trials)
echo "Opção 4: Trabalho oficial (200 trials) - USAR NO RELATÓRIO"
echo "Comando: python3 compare_strategies.py --trials 200 --restarts 50 --iters 1000 --sideways 100 --seed 0"
echo ""

echo "=========================================="
echo "Escolha uma opção (1-4) ou pressione Ctrl+C para cancelar:"
read -p "Opção: " option

case $option in
    1)
        echo "Executando teste rápido..."
        python3 compare_strategies.py --trials 5 --restarts 10 --iters 200 --sideways 30 --seed 99
        ;;
    2)
        echo "Executando teste médio..."
        python3 compare_strategies.py --trials 30 --restarts 20 --iters 500 --sideways 50 --seed 42
        ;;
    3)
        echo "Executando teste completo..."
        python3 compare_strategies.py --trials 100 --restarts 50 --iters 1000 --sideways 100 --seed 42
        ;;
    4)
        echo "Executando trabalho oficial..."
        python3 compare_strategies.py --trials 200 --restarts 50 --iters 1000 --sideways 100 --seed 0
        ;;
    *)
        echo "Opção inválida!"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "EXECUÇÃO CONCLUÍDA"
echo "=========================================="
echo ""
echo "Resultados salvos em: output_comparison/"
echo "  - CSVs: output_comparison/csv/"
echo "  - Gráficos: output_comparison/plots/"
echo ""
echo "Arquivos principais:"
echo "  - output_comparison/csv/comparison_summary.csv (resumo estatístico)"
echo "  - output_comparison/plots/comparison_all_metrics.png (gráfico comparativo)"
