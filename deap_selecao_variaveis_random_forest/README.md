# Otimização de Hiperparâmetros para RandomForestRegressor usando Algoritmos Genéticos

Este notebook demonstra a otimização de hiperparâmetros para um modelo `RandomForestRegressor` utilizando algoritmos genéticos da biblioteca `DEAP` (Distributed Evolutionary Algorithms in Python). O objetivo é encontrar a melhor combinação de hiperparâmetros que minimize o erro do modelo e o tempo de execução no conjunto de dados California Housing.

## Sumário

- [Instalação](#instalação)
- [Conjunto de Dados](#conjunto-de-dados)
- [Otimização com Algoritmos Genéticos](#otimização-com-algoritmos-genéticos)
- [Estrutura dos Hiperparâmetros](#estrutura-dos-hiperparâmetros)
- [Função de Avaliação (Fitness)](#função-de-avaliação-fitness)
- [Execução dos Algoritmos Genéticos](#execução-dos-algoritmos-genéticos)
- [Resultados](#resultados)

## Instalação

As bibliotecas necessárias para executar este notebook são:

- `deap`
- `numpy`
- `scikit-learn`

Elas são instaladas via pip no início do notebook:

```python
!pip install deap
```

## Conjunto de Dados

O dataset utilizado é o **California Housing Prices**, carregado através da biblioteca `scikit-learn` (`fetch_california_housing`). O dataset é dividido em conjuntos de treino, validação e teste para avaliar o desempenho do modelo de forma robusta:

- `x_train`, `y_train`: Para treinamento do modelo.
- `x_train_validation`, `y_train_validation`: Para avaliação do fitness durante a otimização.
- `x_test`, `y_test`: Para avaliação final dos melhores modelos.
- `x_test_validation`, `y_test_validation`: Para avaliação final do EQM dos melhores modelos.

## Otimização com Algoritmos Genéticos

A otimização é realizada utilizando a biblioteca `DEAP`, que fornece uma estrutura flexível para a implementação de algoritmos evolutivos.

### Estrutura dos Hiperparâmetros

Os hiperparâmetros otimizados para o `RandomForestRegressor` incluem:

- `n_estimators`: Número de árvores na floresta.
- `criterion`: Função para medir a qualidade de uma divisão (`'squared_error'`, `'absolute_error'`, `'friedman_mse'`, `'poisson'`).
- `max_depth`: Profundidade máxima da árvore.
- `min_samples_split`: Número mínimo de amostras necessárias para dividir um nó interno.
- `min_samples_leaf`: Número mínimo de amostras necessárias para estar em um nó folha.
- `max_features`: Número de características a considerar ao procurar a melhor divisão (`'sqrt'`, `'log2'`, `None`).

A função `gerar_hiperparametros()` é responsável por gerar um indivíduo (conjunto de hiperparâmetros) de forma aleatória.

### Função de Avaliação (Fitness)

A função `evaluate(individuo)` calcula o fitness de um indivíduo. Ela faz o seguinte:

1.  Instancia um `RandomForestRegressor` com os hiperparâmetros do `individuo`.
2.  Treina o modelo com `x_train` e `y_train`.
3.  Calcula o Erro Quadrático Médio (EQM) no conjunto de validação (`x_train_validation`, `y_train_validation`).
4.  Mede o tempo de execução do treinamento e previsão.
5.  O fitness (custo) é definido como a raiz quadrada do EQM somado ao tempo de execução, buscando minimizar ambos.

### Operadores Genéticos

-   **Seleção**: `tools.selTournament` (torneio com `tournsize=3`).
-   **Crossover**: `tools.cxOnePoint` (crossover de um ponto).
-   **Mutação**: `funcao_mutacao` que substitui aleatoriamente alguns hiperparâmetros do indivíduo por novos valores gerados aleatoriamente.

## Execução dos Algoritmos Genéticos

Dois algoritmos genéticos foram utilizados para otimização:

1.  **`eaSimple`**: Um algoritmo genético básico (`ngen=20`, `cxpb=1`, `mutpb=0.1`).
2.  **`eaMuCommaLambda`**: Um algoritmo mais avançado que gera `lambda_` filhos a partir de `mu` pais, e a próxima geração é selecionada apenas entre os `lambda_` filhos (`mu=90`, `lambda_=100`, `ngen=20`, `cxpb=0.7`, `mutpb=0.3`).

Ambos os algoritmos utilizam um `HallOfFame` (`hof`) para armazenar os 10 melhores indivíduos encontrados ao longo de todas as gerações.

## Resultados

Após a execução de cada algoritmo, os melhores indivíduos (conjuntos de hiperparâmetros) encontrados no `HallOfFame` são avaliados. Para cada indivíduo no `hof`, o modelo `RandomForestRegressor` correspondente é treinado com os dados de teste (`x_test`, `y_test`) e o Erro Quadrático Médio (EQM) é calculado no conjunto de `x_test_validation`, `y_test_validation` para uma avaliação final do desempenho.
