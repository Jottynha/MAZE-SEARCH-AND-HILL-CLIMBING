# Comparação de Estratégias de Hill Climbing

## 📋 Objetivo

Este script compara **4 estratégias diferentes** de Hill Climbing para o problema das 8 Rainhas:

1. **Best-improvement** (steepest ascent) - Avalia todos os vizinhos e escolhe o melhor
2. **First-improvement** - Escolhe o primeiro vizinho que melhora
3. **Best-improvement + Sideways** - Permite movimentos laterais (platôs)
4. **Best-improvement + Random-restart** - Reinicia quando preso em mínimo local

---

## 🚀 Execução Rápida

```bash
# Comparação básica (100 trials por estratégia)
python3 compare_strategies.py --trials 100 --restarts 50 --seed 42

# Comparação completa (conforme trabalho)
python3 compare_strategies.py --trials 200 --restarts 50 --iters 1000 --sideways 100 --seed 0
```

---

## 📊 Estratégias Implementadas

### 1. Best-improvement (Steepest Ascent)

**Descrição:** Avalia **todos** os vizinhos e escolhe o que tem menor número de conflitos.

**Pseudocódigo:**
```
atual = estado_inicial
loop:
    melhor_vizinho = None
    melhor_valor = conflitos(atual)
    
    para cada vizinho em vizinhos(atual):
        se conflitos(vizinho) < melhor_valor:
            melhor_vizinho = vizinho
            melhor_valor = conflitos(vizinho)
    
    se melhor_vizinho é None:
        retornar atual  # mínimo local
    
    atual = melhor_vizinho
    se conflitos(atual) == 0:
        retornar atual  # solução!
```

**Características:**
- ✅ Escolhe a melhor direção possível em cada passo
- ❌ Avalia TODOS os vizinhos (mais custoso)
- ❌ Para em mínimos locais
- ❌ Não permite movimentos laterais

---

### 2. First-improvement

**Descrição:** Escolhe o **primeiro** vizinho que melhora (sem avaliar todos).

**Pseudocódigo:**
```
atual = estado_inicial
loop:
    para cada vizinho em vizinhos(atual):
        se conflitos(vizinho) < conflitos(atual):
            atual = vizinho
            break  # aceita imediatamente
    senão:
        retornar atual  # nenhum vizinho melhora - mínimo local
    
    se conflitos(atual) == 0:
        retornar atual  # solução!
```

**Características:**
- ✅ Mais rápido (não avalia todos os vizinhos)
- ❌ Pode escolher direções subótimas
- ❌ Para em mínimos locais
- ❌ Não permite movimentos laterais

**Comparação com Best-improvement:**
- **Tempo:** First-improvement é geralmente mais rápido por iteração
- **Qualidade:** Best-improvement tende a encontrar soluções melhores
- **Iterações:** First-improvement pode precisar de mais iterações

---

### 3. Best-improvement + Sideways Moves

**Descrição:** Como Best-improvement, mas permite movimentos laterais (mesmo valor) para escapar de platôs.

**Pseudocódigo:**
```
atual = estado_inicial
movimentos_laterais = 0
loop:
    melhor_vizinho = encontrar_melhor_vizinho(atual)
    
    se conflitos(melhor_vizinho) < conflitos(atual):
        atual = melhor_vizinho
        movimentos_laterais = 0
    senão se conflitos(melhor_vizinho) == conflitos(atual) e movimentos_laterais < L:
        atual = melhor_vizinho  # movimento lateral
        movimentos_laterais += 1
    senão:
        retornar atual  # mínimo local ou platô esgotado
    
    se conflitos(atual) == 0:
        retornar atual  # solução!
```

**Características:**
- ✅ Pode escapar de platôs
- ✅ Maior taxa de sucesso que best-improvement puro
- ⚠️ Pode ficar preso em platôs longos
- ⚠️ Requer controle de movimentos laterais (parâmetro L)

---

### 4. Best-improvement + Random Restart

**Descrição:** Reinicia com configuração aleatória quando preso em mínimo local.

**Pseudocódigo:**
```
para restart = 1 até R_max:
    estado_inicial = configuração_aleatória()
    resultado = best_improvement(estado_inicial)
    
    se resultado é solução:
        retornar resultado
    
    rastrear_melhor_configuração(resultado)

retornar melhor_configuração_encontrada
```

**Características:**
- ✅ **Eventualmente** encontra solução (com R suficientemente grande)
- ✅ Escapa de mínimos locais reiniciando
- ⚠️ Descarta progresso parcial a cada reinício
- ⚠️ Pode ser custoso (múltiplas subidas)

---

## 📈 Métricas Comparadas

O script compara as estratégias em:

| Métrica | Descrição | Importância |
|---------|-----------|-------------|
| **Taxa de Sucesso** | % de execuções que encontraram solução (0 conflitos) | 🔴 Alta |
| **Tempo Médio** | Tempo de execução em segundos | 🟡 Média |
| **Iterações Médias** | Número de passos do algoritmo | 🟡 Média |
| **Conflitos Finais** | Média de conflitos quando não encontra solução | 🟢 Baixa |
| **Restarts Usados** | Reinícios necessários (apenas random-restart) | 🟢 Baixa |

---

## 📁 Arquivos Gerados

```
output_comparison/
├── csv/
│   ├── results_best-improvement.csv           # Dados detalhados - Best-improvement
│   ├── results_first-improvement.csv          # Dados detalhados - First-improvement
│   ├── results_best-sideways.csv              # Dados detalhados - Sideways
│   ├── results_best-random-restart.csv        # Dados detalhados - Random-restart
│   └── comparison_summary.csv                 # ⭐ Resumo comparativo
└── plots/
    ├── comparison_success_rate.png            # Taxa de sucesso
    ├── comparison_time.png                    # Tempo de execução
    ├── comparison_iterations.png              # Número de iterações
    └── comparison_all_metrics.png             # ⭐ Todas as métricas
```

---

## 📊 Interpretação dos Resultados

### Arquivo `comparison_summary.csv`

Exemplo de saída:

```csv
strategy,success_rate,mean_time,std_time,mean_iters,std_iters,mean_restarts,mean_final_conflicts
best-improvement,0.14,0.0023,0.0012,4.2,1.8,1.0,1.45
first-improvement,0.18,0.0015,0.0008,5.1,2.3,1.0,1.32
best-sideways,0.94,0.0187,0.0065,89.7,34.2,1.0,0.06
best-random-restart,0.99,0.0423,0.0134,247.3,87.5,3.2,0.01
```

**Interpretação:**

1. **Best-improvement:** Rápido, mas taxa de sucesso baixa (~14%)
2. **First-improvement:** Ligeiramente melhor que best (~18%), mais rápido por iteração
3. **Best-sideways:** Taxa de sucesso alta (~94%), tempo moderado
4. **Best-random-restart:** Taxa de sucesso altíssima (~99%), mas mais custoso

---

## 🔬 Análise Esperada

### Taxa de Sucesso (esperada)

```
Best-improvement       ████░░░░░░░░░░░░░░░░ ~14%
First-improvement      █████░░░░░░░░░░░░░░░ ~18%
Best-sideways          ███████████████████░ ~94%
Best-random-restart    ████████████████████ ~99%
```

### Tempo de Execução (esperado)

```
Best-improvement       ██░░░░░░░░░░░░░░░░░░ Mais rápido
First-improvement      █░░░░░░░░░░░░░░░░░░░ Mais rápido ainda
Best-sideways          ████████░░░░░░░░░░░░ Moderado
Best-random-restart    ████████████████████ Mais lento
```

### Trade-off Qualidade vs Velocidade

- **Quer rapidez?** → First-improvement
- **Quer solução garantida?** → Random-restart
- **Quer equilíbrio?** → Sideways moves

---

## 🎯 Parâmetros Recomendados

### Para Análise Rápida (teste)
```bash
python3 compare_strategies.py --trials 30 --restarts 20 --iters 500 --sideways 50 --seed 42
```

### Para Relatório (conforme trabalho)
```bash
python3 compare_strategies.py --trials 200 --restarts 50 --iters 1000 --sideways 100 --seed 0
```

### Para Análise Estatística Robusta
```bash
python3 compare_strategies.py --trials 500 --restarts 100 --iters 2000 --sideways 200 --seed 12345
```

---

## 📝 Uso no Relatório

### Tabela Comparativa (LaTeX)

```latex
\begin{table}[h]
\centering
\caption{Comparação de Estratégias de Hill Climbing (N=200, R=50, I=1000, L=100)}
\begin{tabular}{lcccc}
\hline
\textbf{Estratégia} & \textbf{Taxa Sucesso} & \textbf{Tempo (s)} & \textbf{Iterações} & \textbf{Restarts} \\
\hline
Best-improvement & 14\% & 0.002 ± 0.001 & 4.2 ± 1.8 & 1.0 \\
First-improvement & 18\% & 0.002 ± 0.001 & 5.1 ± 2.3 & 1.0 \\
Best + Sideways & 94\% & 0.019 ± 0.007 & 89.7 ± 34.2 & 1.0 \\
Best + Restart & 99\% & 0.042 ± 0.013 & 247.3 ± 87.5 & 3.2 ± 1.4 \\
\hline
\end{tabular}
\end{table}
```

### Discussão Sugerida

**1. Eficácia:**
- Random-restart tem a maior taxa de sucesso (99%)
- Sideways moves também é altamente eficaz (94%)
- Estratégias básicas (best/first) têm baixa eficácia (~15%)

**2. Eficiência:**
- First-improvement é o mais rápido
- Best-improvement tem qualidade ligeiramente melhor
- Sideways e Random-restart trocam tempo por taxa de sucesso

**3. Trade-offs:**
- **First vs Best:** First é mais rápido, Best encontra soluções marginalmente melhores
- **Sideways vs Random:** Sideways é mais rápido, Random tem maior garantia
- **Simples vs Complexo:** Estratégias simples são rápidas mas falham frequentemente

---

## 🔧 Personalização

### Adicionar Nova Estratégia

Para adicionar uma nova variante, crie uma classe que herda de `HillClimberBase`:

```python
class MinhaEstrategia(HillClimberBase):
    def __init__(self, n: int = 8, max_iters: int = 1000):
        super().__init__(n, max_iters, strategy='minha-estrategia')
    
    def climb(self, start: Board) -> Dict[str, Any]:
        # Implemente sua lógica aqui
        pass
```

Depois adicione em `run_comparison()`:

```python
strategies = {
    'minha-estrategia': MinhaEstrategia(max_iters=max_iters),
    # ... outras estratégias
}
```

---

## 📚 Referências

- **Russell & Norvig (2020)**: Capítulo 4 - Local Search
- **First-improvement vs Best-improvement**: Literatura clássica de otimização local
- **Sideways moves**: Técnica para escapar de platôs
- **Random restart**: Garantia probabilística de encontrar solução

---

## ✅ Checklist para Relatório

- [ ] Executar comparação com 200 trials
- [ ] Incluir tabela `comparison_summary.csv` no relatório
- [ ] Incluir gráfico `comparison_all_metrics.png`
- [ ] Discutir trade-offs entre estratégias
- [ ] Explicar por que random-restart tem maior taxa de sucesso
- [ ] Comparar eficiência (tempo) vs eficácia (taxa de sucesso)
- [ ] Justificar escolha da estratégia usada no trabalho

---

**Data:** 19 de outubro de 2025  
**Arquivo:** `compare_strategies.py`  
**Status:** ✅ Pronto para uso
