# Seleção de Hiperparâmetros com Algoritmos Evolutivos (DEAP)

Otimização automática de hiperparâmetros de modelos de Machine Learning utilizando Algoritmos Genéticos com a biblioteca **DEAP** aplicados ao dataset **California Housing Prices**.

---

## Visão Geral

Este notebook implementa um pipeline completo de busca evolutiva de hiperparâmetros para três algoritmos de regressão. Em vez de grid search ou random search convencional, utiliza-se um **Algoritmo Genético Customizado** que evolui populações de configurações de hiperparâmetros ao longo de gerações, priorizando modelos com menor RMSE e menor tempo de execução.

---

## Dataset

**California Housing Prices** — obtido via `kagglehub` (Kaggle).

| Etapa de Pré-processamento | Detalhe |
|---|---|
| Imputação de valores ausentes | Média da coluna `total_bedrooms` |
| Engenharia de features | `avg_rooms`, `avg_bedrooms`, `avg_occup` (médias por domicílio) |
| Remoção de colunas brutas | `total_rooms`, `total_bedrooms`, `households` |
| Normalização numérica | `StandardScaler` nas features; `MinMaxScaler` no target |
| Codificação categórica | `OneHotEncoder` na coluna `ocean_proximity` |
| Divisão treino/teste | 60% treino — 40% teste |

---

## Modelos Otimizados

### 1. Random Forest (`RandomForestRegressor`)

Hiperparâmetros buscados:

- `n_estimators` — sequência de Fibonacci (3 a ~233)
- `criterion` — `squared_error`, `friedman_mse`, `poisson`
- `max_depth` — sequência de Fibonacci (2 a ~34)
- `min_samples_split` — `[0.2, 0.1, 0.01, 0.001]`
- `min_samples_leaf` — `[0.2, 0.1, 0.01, 0.001]`
- `max_features` — `sqrt`, `log2`, `None`
- `max_leaf_nodes` — `None` + sequência de Fibonacci

### 2. KNN (`KNeighborsRegressor`)

Hiperparâmetros buscados:

- `n_neighbors` — `[2, 5, 8, 11, 14, 17, 20]`
- `weights` — `uniform`, `distance`
- `algorithm` — `auto`, `ball_tree`, `kd_tree`, `brute`
- `leaf_size` — `[6, 12, 25, 50, 100, 150, 200]`
- `p` (métrica de distância) — `[1, 2, 3, 4]`

### 3. Gradient Boosting (`GradientBoostingRegressor`)

Hiperparâmetros buscados (17 no total), incluindo:

- `loss` — `squared_error`, `absolute_error`, `huber`, `quantile`
- `learning_rate` — de 0.001 a 0.5
- `n_estimators` — sequência de Fibonacci
- `subsample`, `max_depth`, `max_features`, `alpha`, `warm_start`, entre outros

---

## Algoritmo Evolutivo

### Configuração DEAP

| Componente | Configuração |
|---|---|
| **Fitness** | Minimização (peso `-1.0`) |
| **Indivíduo** | Lista de hiperparâmetros gerada aleatoriamente |
| **Cruzamento** | `cxOnePoint` (ponto único) com `cxpb=1.0` |
| **Mutação** | Mutação por gene com `indpb=0.25` |
| **Seleção** | Torneio (`selTournament`) com `tournsize=3` |
| **Hall of Fame** | Top 10 melhores indivíduos |

### Algoritmo Customizado (`eaCustom`)

O algoritmo implementa melhorias em relação ao `eaSimple` padrão do DEAP:

- **População crescente:** a cada geração, `tamanho_inicial + geração × 5` indivíduos são selecionados, expandindo a busca progressivamente.
- **Função de custo composta:** penaliza modelos lentos combinando RMSE com tempo de execução normalizado:
  ```
  custo = RMSE × (1 + tempo_normalizado)
  ```
- **Early stopping:** interrompe a evolução se o melhor fitness não melhorar por 4 gerações consecutivas (`patience=4`).
- **Estatísticas por geração:** média, desvio padrão, mínimo e máximo do fitness.

### Parâmetros de Execução

```python
tamanho_inicial_populacao = 20
aumento_individuos_por_geracao = 5
ngen = 20
cxpb = 1.0   # probabilidade de cruzamento
mutpb = 0.1  # probabilidade de mutação
```

---

## Seleção Final

Após a otimização individual de cada modelo, os **top 10 candidatos** de cada algoritmo (30 no total) são avaliados com **Cross-Validation de 5 folds** usando RMSE como métrica. Os resultados são consolidados em um DataFrame ordenado pela média do CV (`media_cv`), permitindo comparação direta entre modelos de tipos diferentes.

---

## Dependências

```bash
pip install numpy pandas scikit-learn tensorflow deap kagglehub
```

| Biblioteca | Uso |
|---|---|
| `numpy` / `pandas` | Manipulação de dados |
| `scikit-learn` | Modelos ML, pré-processamento, validação |
| `deap` | Framework de algoritmos evolutivos |
| `kagglehub` | Download do dataset |
| `tensorflow` / `keras` | Importado (não utilizado diretamente no fluxo principal) |
| `time` | Medição de tempo de execução dos modelos |

---

## Como Executar

1. Configure suas credenciais do Kaggle (`~/.kaggle/kaggle.json`).
2. Instale as dependências listadas acima.
3. Execute as células em ordem:
   - **Célula 1:** imports e configuração do DEAP
   - **Célula 2:** download e pré-processamento do dataset
   - **Seções RF / KNN / GB:** otimização evolutiva de cada modelo
   - **Seção final:** cross-validation e ranking dos melhores modelos

> **Atenção:** A execução completa pode ser demorada dependendo da configuração de hardware, pois cada indivíduo treina um modelo completo durante a avaliação de fitness.

---

## Estrutura do Notebook

```
deap_selecao_ml.ipynb
├── Imports e configuração DEAP
├── Carregamento e pré-processamento dos dados
├── Random Forest
│   ├── Geração de hiperparâmetros
│   ├── Configuração do toolbox
│   ├── Execução do eaCustom
│   └── Avaliação no conjunto de teste
├── KNN
│   ├── Geração de hiperparâmetros
│   ├── Configuração do toolbox
│   ├── Execução do eaCustom
│   └── Avaliação no conjunto de teste
├── Gradient Boosting
│   ├── Geração de hiperparâmetros
│   ├── Configuração do toolbox
│   ├── Execução do eaCustom
│   └── Avaliação no conjunto de teste
└── Cross-validation e seleção final
```