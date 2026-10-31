# Prompt de referência: implementação assistida por IA das etapas 1 e 2

Registro publicado em **31/10/2026**, a pedido de Matheus Garcia. O roteiro foi elaborado com auxílio do Codex e fornecido como guia para implementar `arvore.py`, `linear.py`, `etapa1.ipynb` e `etapa2.ipynb`. Este documento integra o registro de prompts previsto na seção 13 da especificação (p. 9); sua síntese entrará no apêndice do relatório final.

O texto abaixo preserva integralmente o guia original. As instruções sobre manter o guia interno e alterar somente quatro arquivos descrevem o escopo daquela rodada. A solicitação posterior de registrar o prompt e atualizar a documentação autoriza esta publicação. O histórico, os commits resultantes e a revisão estão em [Uso de IA](../uso-de-ia.md).

SHA-256 do corpo original em UTF-8: `221222a4d29a55e0b3d61183fe559ea7101705f10b6029cc81c2547e6f172396`.

---

# Passo a passo: implementar as etapas 1 e 2 em quatro arquivos

## 1. Escopo e regra de alteração

Este é um roteiro de implementação, não uma implementação dos modelos. O trabalho futuro descrito aqui deve criar ou alterar **somente estes quatro arquivos, na raiz do repositório**:

```text
etapa1.ipynb
etapa2.ipynb
arvore.py
linear.py
```

Reutilizar `utils.py`, o dataset, as divisões de validação e o ambiente já entregues. Não modificar esses componentes. Não criar relatório, arquivos de teste, pastas de resultados, imagens exportadas ou tabelas externas nesta rodada. Os testes serão células dos notebooks; gráficos, tabelas e explicações serão salvos nas próprias saídas dos notebooks. README, requirements, manifests e demais documentos permanecem inalterados.

O relatório será escrito ao final. Para preservar os requisitos que ele deverá conter, deixar os cálculos e explicações correspondentes nos notebooks, prontos para aproveitamento posterior.

Este guia é material interno de trabalho e fica em `.local/`, fora do versionamento, conforme a separação já adotada entre planejamento e entrega acadêmica.

## 2. O que já está preparado

O repositório é `mh131105/fia-queimadas-amazonia`. O diretório local é `/Users/matheus/Documents/ChatGPT/tp2 - FIA`.

| Componente pronto | Como utilizar |
|---|---|
| `utils.py` | Importar `ATRIBUTOS`, `carregar_dados`, `iterar_folds` e `preparar_particao` |
| Desenvolvimento de 2024 | `carregar_dados(2024)`: 140.346 registros |
| Teste externo de 2025 | Reservado para a avaliação final; não abrir nos notebooks desta rodada |
| Cinco folds espaciais | `iterar_folds(dados, "espacial")`; municípios separados entre treino e validação |
| Cinco folds temporais | `iterar_folds(dados, "temporal")`; diagnóstico complementar já previsto no projeto |
| Ambiente | Kernel Jupyter **FIA (Python 3.12)**, com as dependências instaladas |

Os seis atributos, na ordem definida em `ATRIBUTOS`, são:

```python
["numero_dias_sem_chuva", "precipitacao", "lat", "lon", "mes", "hora_utc"]
```

**Alvo contínuo:** `frp`, em MW. **Alvo binário:** FRP maior ou igual ao percentil 75 do treino corrente. O problema caracteriza focos já detectados; não representa previsão antecipada de surgimento de incêndio.

Cada chamada a `preparar_particao` devolve:

| Campo | Conteúdo |
|---|---|
| `X_treino`, `X_avaliacao` | DataFrames com somente os seis atributos, já preparados |
| `y_reg_treino`, `y_reg_avaliacao` | FRP contínua |
| `y_cls_treino`, `y_cls_avaliacao` | Classes 0/1 com o mesmo limiar do treino |
| `limiar_frp` | Percentil 75 do treino usado nessa divisão |
| `parametros` | Medianas e parâmetros da representação escolhida |

Representações disponíveis: `"numerica"` imputa e mantém unidades; `"padronizada"` imputa e aplica média/desvio do treino; `"discretizada"` imputa e divide cada atributo pela mediana do treino, em categorias 0/1. O módulo de aprendizado recebe os dados já preparados e não deve recalcular esses parâmetros.

O valor **58,4 MW** corresponde ao Q75 de todo 2024 e será pertinente ao ajuste final. Não o fixar nos cinco folds: usar o `limiar_frp` devolvido para cada treino. O limiar de **0,5** usado na previsão logística se refere à probabilidade de classe, não à FRP em MW.

## 3. Ordem de trabalho

1. Implementar `arvore.py`.
2. Montar, executar e validar `etapa1.ipynb`.
3. Implementar `linear.py`.
4. Montar, executar e validar `etapa2.ipynb`.

Os módulos devem conter os algoritmos. Os notebooks devem importar os módulos, conduzir os experimentos, comparar com as bibliotecas e explicar os resultados. Evitar copiar a mesma implementação para dentro do notebook e do módulo.

NumPy e a biblioteca padrão podem apoiar as contas dos módulos. O ajuste dos modelos próprios não deve ser delegado a scikit-learn, SciPy ou rotinas de solução pronta. As classes do scikit-learn entram nas células de comparação dos notebooks.

## 4. Implementar `arvore.py`

### 4.1. Definir as interfaces

Adotar estas interfaces, ou manter equivalentes consistentes em todo o notebook:

```python
def entropia(y):
    """Retorna um escalar em bits."""

def ganho_informacao(atributo, y):
    """Recebe uma coluna categórica 1D e suas classes."""

def aprender_arvore(X, y, profundidade_maxima=None):
    """Recebe X 2D e y 1D; devolve a raiz da árvore."""

def predizer(arvore, X):
    """Devolve um array 1D de classes 0/1."""
```

As assinaturas acima são um contrato sugerido, não corpos de funções prontos. A recursão interna pode receber atributos disponíveis, profundidade e classe majoritária do pai.

### 4.2. Implementar a entropia

1. Contar exemplos de cada classe.
2. Converter contagens em proporções.
3. Desconsiderar proporções zero no logaritmo.
4. Calcular `H = -sum(p * log2(p))`.
5. Para conjunto vazio, retornar 0.

### 4.3. Implementar o ganho

1. Calcular a entropia do conjunto pai.
2. Separar os exemplos por valor do atributo.
3. Calcular a média das entropias dos filhos ponderada por seus tamanhos.
4. Retornar `ganho = H_pai - sum((n_filho / n_pai) * H_filho)`.

Não usar medidas de impureza do scikit-learn para implementar essas funções.

### 4.4. Definir a estrutura dos nós

Uma representação com dicionários é suficiente. Guardar em cada nó:

- Quantidade de exemplos e contagem das classes 0/1.
- Classe majoritária, inclusive em nós internos.
- Indicação de folha ou nó de decisão.
- Nas decisões: índice original do atributo, ganho escolhido e filhos por categoria.
- Nas folhas: classe prevista.

Guardar contagens e o ganho permitirá explicar os três primeiros níveis no notebook. Não é necessário criar um sistema genérico de serialização.

### 4.5. Implementar a recursão ID3

1. Validar dimensões, quantidade de exemplos e classes.
2. Se todas as classes forem iguais, criar folha.
3. Se não restarem atributos, criar folha com a maioria.
4. Se atingir a profundidade máxima configurada, criar folha com a maioria.
5. Calcular o ganho de todos os atributos ainda disponíveis.
6. Escolher o maior ganho. Em empate, usar uma regra determinística, como a ordem original dos atributos.
7. Criar os filhos por categoria e repetir o processo, removendo o atributo escolhido da lista disponível.
8. Manter os índices originais de X durante a recursão, para evitar consultar a coluna errada na previsão.

Na maioria empatada, adotar uma convenção fixa, por exemplo classe 0, e documentá-la. Uma entrada inicial vazia pode gerar erro claro; uma eventual partição recursiva vazia usa a maioria do pai.

**Ganho zero não obriga encerrar a árvore:** o pseudocódigo do professor continua a escolher um atributo enquanto houver atributos e as outras condições permitirem. Isso permite aprender problemas como XOR. Se futuramente acrescentar parada por ganho mínimo, identificá-la como pré-poda; não aplicá-la silenciosamente ao modelo apresentado como sem poda.

Definir raiz com profundidade 0. Assim, os três primeiros níveis a explicar são profundidades 0, 1 e 2.

### 4.6. Implementar a previsão

Para cada linha, percorrer os nós pelo valor do atributo até uma folha. Se surgir uma categoria sem filho, retornar a maioria armazenada no nó atual. Retornar apenas um array de classes, na mesma ordem das linhas recebidas.

## 5. Construir `etapa1.ipynb`, célula por célula

### Célula 1 — Problema e objetivo (Markdown)

Explicar a classificação de potência elevada entre focos já detectados, o recorte INPE/Amazônia/AQUA_M-T, os seis atributos e a regra Q75 do treino. Registrar que FRP elevada não é uma classificação oficial de dano ambiental.

### Célula 2 — Imports e seed (código)

Importar NumPy, pandas, matplotlib, as quatro funções de `arvore.py`, os utilitários existentes e `DecisionTreeClassifier`. As métricas podem vir de `sklearn.metrics`.

Definir explicitamente `np.random.seed(42)`. Usar `random_state=42` nas referências que ofereçam essa opção.

### Célula 3 — Verificações didáticas (código)

Criar pequenos exemplos **sintéticos e identificados como tais**, sem misturá-los ao dataset oficial. Verificar com `assert` ou `np.isclose`:

1. Entropia de classes puras igual a 0.
2. Entropia de `[0, 1]` igual a 1 bit.
3. Atributo `[0, 0, 1, 1]` com classes `[0, 0, 1, 1]` produz ganho de 1 bit.
4. Árvore sem limite aprende essa separação perfeitamente no exemplo didático.
5. Árvore sem limite aprende XOR: X igual a `[[0,0], [0,1], [1,0], [1,1]]`, y igual a `[0,1,1,0]`.
6. Categorias não vistas recebem a maioria do nó, sem erro.

Essas verificações ficam no notebook. Não criar arquivos em `tests/` nesta rodada.

### Célula 4 — Carregar o desenvolvimento (código)

```python
dados = carregar_dados(2024)
assert len(dados) == 140346
assert dados["ano"].eq(2024).all()
```

Mostrar um resumo das seis colunas. Não reconstruir o dataset, preencher ausências globalmente nem carregar 2025.

### Célula 5 — Entender uma divisão (código)

```python
fold, treino, validacao = next(iterar_folds(dados, "espacial"))
p = preparar_particao(treino, validacao, "discretizada")
X_treino = p.X_treino.to_numpy()
X_validacao = p.X_avaliacao.to_numpy()
y_treino = p.y_cls_treino.to_numpy()
y_validacao = p.y_cls_avaliacao.to_numpy()
```

Mostrar tamanhos, `p.limiar_frp`, cortes dos atributos em `p.parametros` e contagens de classe. Conferir que X tem seis colunas binárias. Essa célula é exploratória; a avaliação principal percorre os cinco folds.

### Célula 6 — Comparação em cinco folds (código)

Para cada par produzido por `iterar_folds(dados, "espacial")`:

1. Preparar a partição dentro do loop, com representação discretizada.
2. Ajustar a árvore própria usando apenas o treino.
3. Ajustar `DecisionTreeClassifier(criterion="entropy", random_state=42)` nos mesmos X/y.
4. Usar a mesma profundidade máxima nas duas versões quando comparar árvores limitadas; `None` nas duas quando comparar sem poda.
5. Prever a validação em ambas.
6. Calcular acurácia, precisão, recall e F1 da classe 1; usar `zero_division=0` quando apropriado.
7. Calcular a referência que sempre prevê a classe majoritária do treino.
8. Acumular resultados em uma lista e exibir um DataFrame no notebook, com fold, modelo, limiar e métricas.

Não compartilhar a árvore ajustada de um fold com outro. Não usar um Q75 global para construir as classes de todos os folds.

### Célula 7 — Resumo da comparação (código e Markdown)

Apresentar as métricas por fold e média/desvio-padrão por modelo. Identificar o desvio usado, por exemplo amostral com `ddof=1`. Mostrar pelo menos uma matriz de confusão de uma validação identificada.

Diferenças entre as árvores podem ocorrer por desempate e estratégia de divisão. Não exigir estruturas ou acurácias idênticas. Se explorar profundidades 3, 4 e 5, usar somente 2024 e identificar a comparação como seleção por validação. As faixas do gabarito do PDF não são metas a fabricar.

### Célula 8 — Cálculos dos três primeiros níveis (código e Markdown)

Escolher uma árvore e um treino de fold identificados. Para cada nó existente nas profundidades 0, 1 e 2:

1. Apresentar n, n0, n1 e a expressão de H com os valores substituídos.
2. Apresentar contagens dos filhos para o atributo de divisão.
3. Mostrar a soma ponderada e o ganho, com a conta explícita.
4. Mostrar os ganhos dos atributos candidatos para justificar a escolha.
5. Se um ramo terminar em folha antes do terceiro nível, explicar a condição de parada.

As contagens podem ser obtidas programaticamente. A explicação deve desenvolver as contas, em vez de apenas imprimir valores produzidos por uma biblioteca. Tudo fica no notebook, para transposição ao relatório final.

### Célula 9 — Monotonicidade (código e Markdown)

Preparar a explicação de aproximadamente meia página solicitada pelo PDF. Mostrar uma conclusão aprendida que muda após acrescentar um exemplo e reajustar a árvore, mantendo fixa a definição das classes na demonstração.

Um exemplo sintético possível, adotando desempate pela classe 0: começar com X `[[0], [0], [1]]` e y `[0, 1, 1]`. O ramo X=0 empata e prevê 0. Acrescentar X=0 com y=1; após reaprender, esse ramo prevê 1. Identificar o exemplo como didático, não como evidência sobre incêndios reais.

Explicar que se trata de revisão de uma hipótese indutiva com novos dados; isso não demonstra que a consequência lógica clássica deixou de ser monotônica.

### Célula 10 — Diagnóstico temporal complementar (código)

Repetir o mesmo procedimento com `iterar_folds(dados, "temporal")`, se executar o diagnóstico temporal já preparado para o projeto. Mantê-lo em uma tabela separada da avaliação espacial. Os dois protocolos medem dificuldades diferentes e não devem ser agregados como dez folds de um único teste.

### Célula 11 — Discussão (Markdown)

Escrever 2–3 parágrafos sobre o que foi feito, por que as escolhas são adequadas e o que os resultados efetivamente mostraram. Incluir o desequilíbrio de classes, a referência de maioria e as limitações dos atributos/detecções. Não antecipar resultados ainda não executados.

### Célula 12 — Conferência final

Reiniciar o kernel, executar todas as células em ordem e salvar `etapa1.ipynb` com as saídas finais. Figuras e tabelas devem permanecer incorporadas ao notebook.

## 6. Implementar `linear.py`

### 6.1. Definir interfaces e convenções

Adotar arrays NumPy como entrada. X tem forma `(n, d)` sem coluna de intercepto; y tem forma `(n,)`. Adicionar a coluna de 1 internamente quando necessário. O vetor de coeficientes segue `[intercepto, coef_1, ..., coef_d]`.

```python
def ajustar_univariada(x, y):
    """Devolve np.array([intercepto, inclinacao])."""

def ajustar_linear(X, y, taxa_aprendizado, max_iter, tolerancia, lambda_l2=0.0):
    """Devolve (coeficientes, historico_de_perda). Serve à multivariada e Ridge."""

def prever_regressao(X, coeficientes):
    """Devolve FRP estimada como array 1D."""

def sigmoide(z):
    """Devolve probabilidades de maneira numericamente estável."""

def ajustar_logistica(X, y, taxa_aprendizado, max_iter, tolerancia):
    """Devolve (coeficientes, historico_de_perda), sem regularização nesta comparação."""

def prever_probabilidade(X, coeficientes):
    """Devolve P(classe 1)."""

def prever_classe(X, coeficientes, limiar=0.5):
    """Devolve (probabilidade >= limiar).astype(int)."""
```

Funções auxiliares pequenas podem ficar no próprio `linear.py`. Nenhum módulo adicional é necessário.

### 6.2. Regressão univariada por fórmula fechada

Calcular:

```text
b1 = sum((x - media_x) * (y - media_y)) / sum((x - media_x)**2)
b0 = media_y - b1 * media_x
```

Se x for constante, adotar inclinação 0 e intercepto igual à média de y, com esse caso documentado. Não chamar `LinearRegression` para obter os coeficientes próprios.

### 6.3. Regressão multivariada por gradiente

Seja Xb a matriz com intercepto e beta o vetor de parâmetros. Implementar a função objetivo:

```text
J(beta) = sum((Xb @ beta - y)**2) / (2*n)
```

Gradiente e atualização:

```text
erro = Xb @ beta - y
gradiente = Xb.T @ erro / n
beta = beta - taxa_aprendizado * gradiente
```

Inicializar beta com zeros. Usar operações vetorizadas, registrar a perda, limitar iterações e definir uma parada clara, como melhoria relativa pequena por um número de iterações ou norma do gradiente pequena. Guardar a iteração efetivamente atingida pelo tamanho do histórico. Se houver divergência ou valores não finitos, sinalizar o problema e rever a taxa usando somente o desenvolvimento.

Não substituir o gradiente por inversão de matriz, `lstsq`, otimizador pronto ou `fit` de biblioteca.

### 6.4. Ridge L2 na mesma implementação

Adotar e documentar esta convenção:

```text
J(beta) = sum(erro**2)/(2*n) + (lambda_l2/2) * sum(beta[1:]**2)
gradiente = Xb.T @ erro/n + lambda_l2 * [0, beta[1], ..., beta[d]]
```

O intercepto não recebe penalização. Com `lambda_l2=0`, recuperar a regressão multivariada anterior.

Comparar adicionalmente com `Ridge` é opcional na especificação. Se fizer a conferência, a [convenção do scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html) usa soma dos quadrados mais `alpha * norma²`. Multiplicando o objetivo definido acima por `2*n`, a equivalência é **`alpha = n * lambda_l2`**. Não comparar os mesmos valores numéricos de alpha e lambda como se os objetivos fossem iguais.

### 6.5. Logística por gradiente

1. Calcular `z = Xb @ beta`.
2. Implementar a sigmoide estável: para z não negativo, usar `1/(1+exp(-z))`; para z negativo, usar `exp(z)/(1+exp(z))`.
3. Calcular a perda binária pela expressão estável `mean(logaddexp(0, z) - y*z)`.
4. Calcular `gradiente = Xb.T @ (sigmoide(z) - y) / n`.
5. Atualizar por descida de gradiente, com histórico e parada explícita.
6. Classificar com probabilidade maior ou igual a 0,5.

Nesta comparação principal, implementar a logística sem penalização. Na referência instalada do scikit-learn 1.9.1, usar **`C=np.inf`**, que desativa a regularização, conforme a [documentação oficial](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html). Manter o valor padrão `C=1` compararia objetivos diferentes.

## 7. Construir `etapa2.ipynb`, célula por célula

### Célula 1 — Objetivos (Markdown)

Apresentar as duas tarefas: estimar FRP em MW e classificar FRP elevada com a mesma definição da etapa 1. Identificar os seis atributos e o atributo univariado escolhido: dias sem chuva.

### Célula 2 — Imports e seed (código)

Importar as funções de `linear.py`, os utilitários existentes, NumPy, pandas, matplotlib e `LinearRegression`/`LogisticRegression`. Importar métricas como `r2_score`, `mean_absolute_error`, `mean_squared_error`, `accuracy_score`, precisão, recall e F1.

Definir `np.random.seed(42)`. Usar `np.sqrt(mean_squared_error(y, pred))` para RMSE, ou a função específica compatível com a versão instalada.

### Célula 3 — Verificações didáticas (código)

Manter os testes neste notebook, com dados sintéticos identificados:

1. Para x `[0,1,2]` e y `[1,3,5]`, a fórmula fechada retorna intercepto 1 e inclinação 2.
2. Com x constante, o caso definido no módulo funciona sem divisão por zero.
3. O gradiente de um pequeno exemplo confere com diferenças finitas: `(J(beta+eps*ej)-J(beta-eps*ej))/(2*eps)`, incluindo o intercepto e a regularização.
4. A multivariada converge em um exemplo linear simples, dentro de tolerância numérica declarada.
5. Ridge com lambda zero coincide com o objetivo linear; lambda elevado tende a reduzir a norma dos pesos, sem penalizar diretamente o intercepto. Não exigir monotonicidade individual de todos os coeficientes.
6. `sigmoide(0)` é 0,5; entradas de grande magnitude não geram infinito/NaN; a perda e o gradiente logísticos são finitos.

Não exigir coeficientes finitos em um limite teórico de infinitas iterações para logística sem regularização em dados perfeitamente separáveis; verificar a execução finita e a perda da implementação.

### Célula 4 — Carregar 2024 (código)

Carregar `dados = carregar_dados(2024)`. Usar os mesmos folds espaciais da etapa 1. Não reutilizar uma partição global já transformada antes de entrar nos folds.

### Célula 5 — Regressão univariada (código)

Em cada fold:

1. Chamar `preparar_particao(treino, validacao, "numerica")`.
2. Selecionar apenas `numero_dias_sem_chuva` de X.
3. Ajustar a fórmula fechada usando `y_reg_treino`.
4. Ajustar `LinearRegression()` com a mesma coluna e os mesmos exemplos. Para o scikit-learn, manter X 2D, com forma `(n, 1)`.
5. Calcular R², MAE e RMSE na validação de ambas as versões.
6. Comparar também com prever sempre a média de FRP do treino.

Apresentar uma tabela por fold e uma síntese por modelo. Os coeficientes univariados dessa representação mantêm interpretação nas unidades originais.

### Célula 6 — Regressão multivariada (código)

Em cada fold, preparar `"padronizada"`, ajustar o gradiente próprio nos seis atributos e comparar com `LinearRegression()` usando exatamente as mesmas matrizes.

A coluna de intercepto é interna à implementação própria. Não acrescentá-la novamente ao X passado para a referência com `fit_intercept=True`.

Mostrar R², MAE e RMSE. Para um fold identificado, apresentar a curva de perda por iteração e discutir a convergência. Diferenças importantes em relação ao mínimo obtido pela biblioteca pedem investigação de gradiente, taxa ou parada.

### Célula 7 — Ridge e curva de coeficientes (código)

1. Definir uma grade de lambdas não negativos antes de avaliar 2025; usar valores positivos espaçados em escala logarítmica e tratar lambda zero separadamente.
2. Ajustar a versão própria usando `lambda_l2`.
3. Para visualizar a curva, manter um treino e a sua padronização fixos enquanto varia lambda.
4. Plotar os seis coeficientes contra lambda, com legenda dos nomes dos atributos; o intercepto pode aparecer separadamente, identificado como não penalizado.
5. Comparar a qualidade das configurações pela validação de 2024, por exemplo usando RMSE médio.
6. Se usar `Ridge` como conferência adicional, aplicar `alpha = len(X_treino) * lambda_l2` e o mesmo X/y.

Os resultados usados para escolher lambda são resultados de seleção por validação. Não apresentá-los como uma avaliação independente realizada depois da escolha.

### Célula 8 — Logística própria e scikit-learn (código)

Em cada fold, preparar `"padronizada"` e usar `y_cls_treino`/`y_cls_avaliacao`, que mantêm a definição da etapa 1. Ajustar a implementação própria e a referência sem regularização, por exemplo:

```python
referencia = LogisticRegression(
    C=np.inf,
    solver="lbfgs",
    fit_intercept=True,
    max_iter=10000,
    tol=1e-9,
    random_state=42,
)
```

Essa configuração é uma referência proposta para o ambiente instalado, não um parâmetro exigido pelo professor. O algoritmo da biblioteca pode usar outro otimizador; comparar objetivos, previsões, perdas e métricas, sem exigir a mesma trajetória de gradiente.

Apresentar acurácia, precisão, recall e F1 da classe 1, além da referência de maioria e de uma curva de perda do modelo próprio. Usar 0,5 como limite das probabilidades para a comparação principal. Não introduzir pesos de classe em uma versão apenas.

### Célula 9 — Tabelas consolidadas (código)

Exibir no próprio notebook:

- Tabela de regressão: modelo, fold, R², MAE e RMSE; incluir univariada própria/biblioteca, multivariada própria/biblioteca e Ridge próprio.
- Tabela de classificação: modelo, fold, limiar FRP, acurácia, precisão, recall e F1; incluir logística própria/biblioteca e maioria.
- Médias e desvios por modelo, deixando explícito o que foi selecionado usando a validação.

Valores de R² negativos ou desempenhos abaixo das faixas ilustrativas do PDF devem ser reportados como observados. Não trocar exemplos, métricas ou recortes para atingir um resultado esperado.

### Célula 10 — Diagnóstico temporal complementar (código)

Se executar o protocolo temporal preparado no projeto, repetir as comparações com `iterar_folds(dados, "temporal")`, reaprendendo todos os parâmetros de preparação em cada treino. Manter os resultados temporais separados dos espaciais.

### Célula 11 — Discussão (Markdown)

Escrever 2–3 parágrafos sobre método, justificativas e aprendizados observados. Discutir cauda longa da FRP, limites de relações lineares, convergência, regularização, desequilíbrio de classes e diferenças entre versões próprias e bibliotecas.

### Célula 12 — Conferência final

Reiniciar o kernel, executar tudo e salvar `etapa2.ipynb` com as saídas. Não criar arquivos externos para curvas, tabelas ou métricas nesta rodada.

## 8. Conferência antes de concluir os quatro arquivos

- [ ] Somente `arvore.py`, `linear.py`, `etapa1.ipynb` e `etapa2.ipynb` foram criados/alterados na implementação.
- [ ] Os módulos contêm algoritmos próprios; bibliotecas prontas aparecem nas comparações dos notebooks.
- [ ] As duas versões de cada comparação usam os mesmos exemplos, atributos, classes e preparação.
- [ ] Q75, imputação, escala e discretização são obtidos de cada treino usando `utils.py`.
- [ ] Os cinco folds espaciais foram executados, com média de acurácia da árvore.
- [ ] Os cálculos dos três níveis e a demonstração de revisão da árvore estão no primeiro notebook.
- [ ] Fórmula fechada, gradiente, L2, curva coeficientes × lambda e logística estão no segundo notebook.
- [ ] `LinearRegression` e `LogisticRegression` aparecem explicitamente na etapa 2; a árvore é comparada com `DecisionTreeClassifier` na etapa 1.
- [ ] Testes e gráficos ficam nos próprios notebooks, com exemplos sintéticos identificados.
- [ ] As duas execuções completas funcionam após reiniciar o kernel.
- [ ] 2025 continua reservado; nenhum relatório ou arquivo adicional foi produzido.

Na implementação futura, fazer commits atômicos em português, com a autoria e `Signed-off-by` já combinados, restringindo os arquivos de cada commit a esse conjunto. Uma sequência possível é: implementar a árvore; validar/documentar a etapa 1 no notebook; implementar regressões; validar/documentar a etapa 2 no notebook. Não incluir este guia interno nos commits da entrega.

## 9. Relação com a especificação

| Exigência | Local do PDF | Onde fica nesta rodada |
|---|---|---|
| Árvore do zero e comparação com biblioteca | P. 4, seção 4.2, itens 4 e 5 | `arvore.py` e `etapa1.ipynb` |
| Entropia/ganho nos três primeiros níveis | P. 4, seção 4.2, item 3 | Cálculos no primeiro notebook; relatório ao final |
| Validação cruzada 5-fold e acurácia média | P. 4, seção 4.2, item 6 | Primeiro notebook |
| Meia página sobre monotonicidade | P. 4, seção 4.2, item 7 | Explicação preparada no primeiro notebook; relatório ao final |
| Univariada e multivariada com gradiente | P. 5, seção 5.2, itens 2 e 3 | `linear.py` e segundo notebook |
| L2/Ridge e curva de coeficientes | P. 5, seção 5.2, item 4 | `linear.py` e segundo notebook |
| Logística e comparações com scikit-learn | P. 5, seção 5.2, itens 5 e 6 | `linear.py` e segundo notebook |

O diagnóstico temporal, as métricas complementares e a conferência com `Ridge` devem ser identificados como escolhas do projeto ou verificações adicionais, sem atribuí-los como exigências textuais dessas duas etapas. O relatório LaTeX, os demais módulos do pipeline e as atualizações dos documentos serão tratados em uma rodada posterior.
