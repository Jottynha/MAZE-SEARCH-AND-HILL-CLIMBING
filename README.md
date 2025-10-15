# MAZE-SEARCH

Este projeto implementa e compara o desempenho de diferentes algoritmos de busca para encontrar um caminho em um labirinto. Os algoritmos implementados incluem buscas não informadas (BFS, DFS) e buscas informadas (Gulosa, A*).

## Estrutura do Projeto

-   `main.py`: O script principal para executar os testes, gerar relatórios e gráficos.
-   `data/labirinto.txt`: O arquivo que define a estrutura do labirinto, incluindo paredes, início e fim.
-   `src/`: Contém os módulos principais da lógica de busca.
    -   `search.py`: Implementação dos algoritmos de busca (BFS, DFS, Gulosa, A*).
    -   `maze.py`: Lógica para carregar e representar o labirinto.
    -   `heuristics.py`: Funções de heurística (ex: Distância de Manhattan).
-   `medicoes_desempenho.txt`: Arquivo de saída gerado com os resultados detalhados dos testes.
-   `bench_results/`: Diretório onde os gráficos de desempenho são salvos.

## Pré-requisitos

Para executar este projeto, você precisará do Python 3 e das seguintes bibliotecas:

-   pandas
-   matplotlib
-   numpy

Você pode instalá-las com o pip:

```bash
pip install pandas matplotlib numpy
```

## Como Executar

Para rodar os testes e gerar o relatório, execute o script `main.py` a partir da raiz do projeto:

```bash
python main.py
```

O script irá:
1.  Carregar o labirinto a partir de `data/labirinto.txt`.
2.  Executar cada um dos algoritmos de busca definidos.
3.  Imprimir uma tabela de resumo e os caminhos detalhados no console.
4.  Salvar essa mesma saída no arquivo `medicoes_desempenho.txt`.
5.  Gerar gráficos de barras comparando as métricas de desempenho (tempo, memória, nós expandidos) e salvá-los como imagens `.png` no diretório `bench_results/`.

## Parâmetros e Reprodução

Para garantir a reprodutibilidade dos resultados, os seguintes parâmetros são fixados em `main.py`:

-   **Semente Aleatória**: A semente para geração de números pseudo-aleatórios é fixada em `42` através da função `set_seed(42)`. Isso é importante para algoritmos que possam ter desempates aleatórios.
-   **Labirinto**: O labirinto usado é sempre o `data/labirinto.txt`.
-   **Custo Ótimo de Referência**: A variável `COSTO_MINIMO_OTIMO` em `main.py` é usada para verificar a optimalidade das soluções encontradas. O valor está definido como `5.0`.
-   **Algoritmos**: Os algoritmos a serem testados estão definidos na lista `TESTS` em `main.py`.

Para reproduzir exatamente as tabelas e gráficos do relatório, basta executar o comando `python main.py` novamente. Os arquivos `medicoes_desempenho.txt` e as imagens em `bench_results/` serão sobrescritos com os novos resultados, que devem ser idênticos aos anteriores devido aos parâmetros fixos.
