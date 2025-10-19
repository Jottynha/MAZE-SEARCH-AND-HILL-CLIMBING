# HILL-CLIMBING-8-RAINHAS

Projeto para disciplina de Inteligência Artificial - Implementação de Hill Climbing com Random Restart para o problema das 8 Rainhas.

## Descrição

Este projeto implementa o algoritmo **Hill Climbing com Random Restart** para resolver o problema clássico das 8 Rainhas. O algoritmo busca posicionar 8 rainhas em um tabuleiro de xadrez 8×8 de forma que nenhuma rainha ataque outra.

### Características da Implementação

- **Representação**: Permutações (cada coluna tem exatamente uma rainha)
- **Vizinhança**: Swap de colunas (garante ausência de conflitos por linha)
- **Função objetivo**: Minimizar número de pares de rainhas em conflito
- **Movimentos laterais**: Permitidos (até um limite configurável)
- **Random Restart**: Reinicia a busca com configuração aleatória quando preso em mínimo local

## Como Executar

### Pré-requisitos

```bash
pip install numpy matplotlib
```

### Execução Básica

Para executar com os parâmetros padrão (conforme especificação do trabalho):

```bash
python3 hill_climbing.py --trials 200 --restarts 50 --iters 1000 --sideways 100 --seed 0
```

### Parâmetros

- `--trials N`: Número de execuções independentes (padrão: 30)
- `--restarts R`: Número máximo de reinícios por execução (padrão: 100)
- `--iters I`: Número máximo de iterações por reinício (padrão: 1000)
- `--sideways L`: Número máximo de movimentos laterais consecutivos (padrão: 100)
- `--seed S`: Semente para reprodutibilidade (padrão: 42)
- `--vary-restarts`: Lista de valores de restarts para comparar (ex: `10 50 100 200`)
- `--no-display`: Não exibir janelas de plot (apenas salvar imagens)

### Exemplos de Uso

**Execução única com configuração do trabalho:**
```bash
python3 hill_climbing.py --trials 200 --restarts 50 --iters 1000 --sideways 100 --seed 0
```

**Comparar diferentes números de restarts:**
```bash
python3 hill_climbing.py --vary-restarts 10 50 100 200 --trials 30 --seed 42
```

**Experimento sem exibir janelas (para servidores):**
```bash
python3 hill_climbing.py --trials 100 --restarts 50 --seed 0 --no-display
```

## Resultados e Arquivos Gerados

Todos os resultados são salvos no diretório `output/`:

### Estrutura de Diretórios

```
output/
├── csv/                    # Dados brutos e estatísticas
│   ├── results_summary.csv        # Dados detalhados de cada execução
│   ├── statistics_summary.csv     # Estatísticas agregadas
│   └── summary_restarts_*.csv     # Estatísticas por valor de restart
├── boxplot/                # Boxplots de métricas
│   └── box_times.png
├── histogram/              # Histogramas de distribuição
│   └── hist_iters.png
├── plots/                  # Gráficos comparativos
│   └── success_vs_restarts.png
└── solutions/              # Visualizações de soluções encontradas
    └── solution_trial_*.png
```

### Arquivo CSV Detalhado (`results_summary.csv`)

Contém uma linha por execução com as seguintes colunas:

- `run_id`: ID da execução (1 a N)
- `seed_used`: Semente usada (para reprodutibilidade)
- `success`: Se encontrou solução (True/False)
- `restarts_used`: Número de reinícios necessários
- `total_iterations`: Total de iterações realizadas
- `time_s`: Tempo de execução em segundos
- `final_conflicts`: Número de conflitos na configuração final
- `used_sideways`: Movimentos laterais usados no último reinício
- `solution`: Configuração final (lista de posições)

### Arquivo de Estatísticas (`statistics_summary.csv`)

Contém estatísticas agregadas:

- `total_runs`: Total de execuções
- `success_rate`: Taxa de sucesso (0 a 1)
- `mean_time`, `median_time`, `std_time`: Estatísticas de tempo
- `mean_iters`, `median_iters`, `std_iters`: Estatísticas de iterações
- `mean_restarts`, `median_restarts`, `std_restarts`: Estatísticas de reinícios
- `mean_final_conflicts`, `median_final_conflicts`, `std_final_conflicts`: Estatísticas de conflitos

## Reprodutibilidade

### Reproduzir Todas as Execuções

Para reproduzir exatamente os mesmos resultados, use a mesma seed base:

```bash
python3 hill_climbing.py --trials 200 --restarts 50 --iters 1000 --sideways 100 --seed 0
```

### Reproduzir Uma Execução Específica

Para reproduzir a execução `run_id=5`:

1. Consulte o `seed_used` no CSV (ex: seed_used=4 se seed base foi 0)
2. Execute com `--trials 1` e essa seed:

```bash
python3 hill_climbing.py --trials 1 --restarts 50 --iters 1000 --sideways 100 --seed 4
```

### Como Funciona a Reprodutibilidade

- Cada execução recebe uma seed única: `seed_used = base_seed + run_id - 1`
- O CSV salva o `seed_used` para cada execução
- Isso permite reproduzir tanto o conjunto completo quanto execuções individuais

## Análise dos Resultados

### Gráficos Principais

1. **Boxplot de Tempos** (`boxplot/box_times.png`): Distribuição dos tempos de execução
2. **Histograma de Iterações** (`histogram/hist_iters.png`): Distribuição do número de iterações
3. **Taxa de Sucesso vs Restarts** (`plots/success_vs_restarts.png`): Como o número de reinícios afeta a taxa de sucesso
4. **Visualizações de Soluções** (`solutions/*.png`): Tabuleiros com soluções encontradas

### Métricas Importantes

- **Taxa de Sucesso**: Percentual de execuções que encontraram solução (0 conflitos)
- **Tempo Médio**: Tempo médio para encontrar solução ou esgotar restarts
- **Iterações Médias**: Número médio de passos do algoritmo
- **Restarts Necessários**: Quantos reinícios foram necessários em média

## Implementação Técnica

### Algoritmo Hill Climbing

```python
# Pseudocódigo
função hill_climbing(estado_inicial):
    atual = estado_inicial
    loop:
        vizinhos = gerar_vizinhos(atual)  # swap de colunas
        melhor = selecionar_melhor(vizinhos)
        
        se melhor é pior que atual:
            retornar atual  # mínimo local
        
        se melhor igual a atual e movimentos_laterais < L:
            movimentos_laterais++
        senão se melhor igual a atual:
            retornar atual  # platô esgotado
        
        atual = melhor
        
        se atual é solução:
            retornar atual
```

### Random Restart

```python
função random_restart(max_restarts):
    para r = 1 até max_restarts:
        estado_inicial = gerar_aleatório()
        resultado = hill_climbing(estado_inicial)
        
        se resultado é solução:
            retornar resultado
    
    retornar melhor_configuração_encontrada
```

## Parâmetros do Trabalho

Conforme especificação:

- **N = 200**: Número de execuções independentes
- **I_max = 1000**: Iterações máximas por reinício
- **R_max = 50**: Reinícios máximos por execução
- **L = 100**: Movimentos laterais máximos consecutivos
- **Seed = 0**: Semente base para reprodutibilidade

## Objetivos de Análise

O experimento permite analisar:

1. **Eficácia**: Qual a taxa de sucesso do algoritmo?
2. **Eficiência**: Quanto tempo/iterações são necessários?
3. **Sensibilidade**: Como o número de restarts afeta o desempenho?
4. **Distribuição**: Como as métricas se distribuem estatisticamente?
5. **Reprodutibilidade**: Os resultados são consistentes entre execuções?

## Referências

- Russell, S., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.)
- Problema das N-Rainhas: Problema clássico de satisfação de restrições
