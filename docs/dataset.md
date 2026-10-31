# Dataset de focos de fogo na Amazônia: guia para os notebooks

Este documento descreve o dataset derivado do Programa Queimadas/INPE, sua auditoria e o uso correto nas etapas do trabalho. A unidade de análise é uma **detecção de fogo em um pixel e horário**, e não um incêndio individual.

## Resumo da versão auditada

Construção a partir dos 24 originais consultados em **31/10/2026**, somando **1.835.123.210 bytes** (aproximadamente 1,84 GB). Foram lidos **11.608.772 registros brasileiros** de todos os sensores; **5.404.226** estavam marcados como bioma Amazônia; **183.477** pertenciam ao AQUA_M-T e formam o dataset entregue. Não foi necessário excluir registros desse último recorte por qualidade do alvo, identificador, data, coordenadas ou duplicação.

| Indicador | Desenvolvimento 2024 | Teste 2025 |
|---|---:|---:|
| Registros | 140.346 | 43.131 |
| Municípios/grupos | 531 | 522 |
| Meses contemplados | 12 | 12 |
| Dias com alguma detecção | 363 | 357 |
| Registros com os seis atributos completos | 138.376 | 40.575 |
| Percentual com atributos completos | 98,60% | 94,07% |
| Dias sem chuva ausentes | 1.970 | 2.556 |
| Precipitação ausente | 0 | 1.278 |
| FRP ausente/inválida no produto | 0 | 0 |

Todas as 24 fontes mensais foram processadas. Um dia sem registros do sensor no recorte não equivale a um dia comprovadamente sem fogo. As contagens de 140.346 e 43.131 também coincidem com as contagens de Amazônia dos produtos anuais de referência auditados anteriormente; é uma conferência agregada entre produtos do próprio INPE, não uma validação independente nem uma comparação linha a linha.

As ausências de precipitação em 2025 concentram-se em março (163 registros), abril (62) e novembro (1.053). Portanto, não se deve presumir ausência aleatória. O procedimento padrão preserva essas linhas e preenche atributos com estatísticas do treino de 2024; a avaliação deverá discutir essa limitação.

**FRP no desenvolvimento de 2024:** mediana de **27,3 MW**, Q75 de **58,4 MW** e máximo de **8.094,3 MW**. Há sete valores iguais a zero, preservados. O limiar de **58,4 MW** é para o ajuste final com todo 2024; os folds espaciais têm limiares de treino entre 57,9 e 59,5 MW. A distribuição de FRP de 2025 não foi resumida.

### Registros por mês

| Mês | 2024 | 2025 |
|---|---:|---:|
| Janeiro | 2.049 | 1.219 |
| Fevereiro | 3.157 | 399 |
| Março | 2.654 | 772 |
| Abril | 1.117 | 293 |
| Maio | 1.670 | 836 |
| Junho | 2.842 | 1.650 |
| Julho | 11.434 | 2.183 |
| Agosto | 38.266 | 6.094 |
| Setembro | 41.463 | 7.211 |
| Outubro | 16.169 | 7.868 |
| Novembro | 14.158 | 9.568 |
| Dezembro | 5.367 | 5.038 |

Os CSVs derivados somam aproximadamente **8,89 MB comprimidos**. A auditoria não encontrou identificadores repetidos nem repetições exatas de coordenadas/horário/sensor. Todos os códigos municipais do recorte têm sete dígitos; nesta versão não foi necessário usar o agrupamento espacial substituto.

## Origem e recorte

- Fonte principal e única das observações: [CSV mensais oficiais do INPE](https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/mensal/Brasil/), associados ao [catálogo indicado para o trabalho](https://dados.gov.br/dados/conjuntos-dados/monitoramento-de-queimadas).
- Período: os 24 meses de janeiro de 2024 a dezembro de 2025, sem amostragem de linhas.
- Filtros: país Brasil, bioma Amazônia e sensor `AQUA_M-T`.
- Desenvolvimento e escolha de modelos: **2024**. Teste externo por ano: **2025**.
- Não foram acrescentados dados de estações do INMET nem detecções de outros sensores. Os atributos meteorológicos presentes nesta versão são os associados aos focos pelo próprio INPE.

O filtro de bioma utiliza a classificação fornecida pelo INPE. Não foi realizado um novo cruzamento com polígonos do IBGE. Os campos do arquivo mensal foram inspecionados diretamente; o produto anual de referência auditado anteriormente não oferece FRP e meteorologia, por isso não é concatenado ao dataset.

## Arquivos entregues

| Arquivo | Uso |
|---|---|
| [desenvolvimento_2024.csv.gz](../data/dataset/desenvolvimento_2024.csv.gz) | Dataset completo de desenvolvimento, com indicação dos folds espaciais |
| [teste_2025.csv.gz](../data/dataset/teste_2025.csv.gz) | Teste externo, sem folds internos; manter reservado durante o desenvolvimento |
| [manifesto do dataset](../data/dataset/manifesto.json) | Contagens, hashes dos produtos e política dos alvos |
| [manifesto das fontes](../data/fontes_2024_2025.json) | URLs, bytes e SHA-256 de cada um dos 24 originais |
| [dicionário de dados](../data/dicionario.csv) | Descrição, unidade, origem e papel das 27 colunas |
| [auditoria completa](auditoria-dataset.json) | Fluxo de filtragem, qualidade, cobertura e diagnóstico dos folds |
| [exclusões](../data/dataset/exclusoes.csv.gz) | Identificador, arquivo, linha e motivo das exclusões; somente cabeçalho se não houver exclusões |
| [utils.py](../utils.py) | Leitura, folds e preparação de X/y, sem implementação dos modelos acadêmicos |

Os CSVs comprimidos são lidos diretamente pelo pandas. Os originais permanecem em `data/raw/`, fora do Git por volume; os dois datasets derivados estão versionados e podem ser utilizados após clonar o repositório, sem baixar todos os originais.

## Atributos e alvos

Os seis atributos principais, nesta ordem, são:

| Atributo | Unidade | Observação |
|---|---|---|
| `numero_dias_sem_chuva` | dias | Valores inteiros não negativos; há ausências preservadas |
| `precipitacao` | mm | Precipitação associada ao instante da detecção |
| `lat` | graus decimais | Latitude do pixel |
| `lon` | graus decimais | Longitude do pixel |
| `mes` | 1 a 12 | Derivado da data UTC |
| `hora_utc` | hora decimal, de 0 até menos de 24 | Hora + minuto/60 + segundo/3600 |

**Regressão:** o alvo é `frp`, em megawatts (MW), mantido na escala original. Os valores extremos válidos não foram aparados e FRP zero não foi transformada automaticamente em ausência.

**Classificação:** o alvo é `frp >= Q75(FRP do treino)`. O percentil usa interpolação linear. O limiar é aprendido separadamente no treino de cada fold e aplicado à respectiva validação. Após escolher o modelo, o ajuste final usa o Q75 de todo 2024 e aplica esse mesmo valor a 2025. Empates podem produzir mais de 25% de positivos.

Não existe uma coluna fixa `frp_elevada` no CSV: calculá-la uma única vez antes da validação faria o limiar depender dos alvos da própria validação. `preparar_particao` devolve o rótulo adequado para cada treino. A classificação é uma definição estatística do trabalho; não é uma escala oficial de gravidade de incêndios.

`frp`, identificadores, códigos municipais, procedência, partição, flags de ausência, `grupo_validacao` e `fold_espacial` **não entram em X**. O índice composto `risco_fogo` foi preservado para contexto, mas também está fora dos seis atributos e não substitui uma probabilidade produzida pelo modelo.

## Limpeza e rastreabilidade

O script de construção executa estas operações, com contagens por arquivo:

1. Confere o hash de cada original e o esquema de 16 colunas.
2. Aplica os filtros de país, bioma e sensor.
3. Valida identificador UUID, data UTC e correspondência entre data e mês do arquivo.
4. Confere coordenadas finitas na faixa ampla do Brasil adotada para integridade: latitude entre -34 e 6, longitude entre -74 e -34. Essa checagem não substitui validação contra uma malha geográfica.
5. Exclui alvos FRP ausentes, não finitos ou negativos. **FRP nunca é imputada.**
6. Converte vazios, -999 e valores fora do domínio em ausências meteorológicas. Dias sem chuva devem ser inteiros não negativos; precipitação deve ser não negativa; risco deve estar entre 0 e 1.
7. Confere duplicatas por identificador e por coordenadas/horário/sensor. Cópias idênticas são removidas com registro; cópias com valores conflitantes interrompem a construção para investigação.
8. Ordena cronologicamente, separa os anos e grava os produtos com origem por linha.

`arquivo_origem`, `linha_origem` e `sha256_origem` permitem reencontrar uma observação no arquivo oficial. `linha_origem` conta registros lógicos do CSV, sendo 1 o cabeçalho; campos com quebras de linha, se existirem, continuam pertencendo a um único registro. Os hashes dos CSVs originais são conferidos antes de qualquer processamento. O registro de exclusões não inclui as linhas descartadas pelos filtros temáticos: essas são contabilizadas no fluxo agregado da auditoria.

### Ausências e transformações

As tabelas entregues mantêm as ausências e duas flags de qualidade, sem preencher o dataset inteiro antecipadamente. A preparação para cada modelo é feita em `utils.py`:

- `numerica`: imputa pela mediana de cada atributo no treino e mantém a escala original.
- `padronizada`: após imputar, aplica média e desvio-padrão populacional aprendidos no treino. Coluna constante usa escala 1.
- `discretizada`: após imputar, divide cada atributo em duas categorias, abaixo da mediana de treino ou maior/igual a ela. Uma coluna constante não produz ganho informativo.

Nenhum parâmetro é recalculado na validação ou no teste. A função devolve as medianas e, quando aplicável, médias, escalas ou cortes usados. As flags de ausência ficam disponíveis para auditoria, sem ampliar automaticamente os seis atributos principais. A análise de casos completos pode ser usada como sensibilidade, mas não se deve presumir que a ausência é aleatória.

As representações entregues usam mês e hora em valores numéricos originais. Codificação cíclica é uma alternativa a estudar somente no desenvolvimento, com o mesmo protocolo nas comparações; não foi aplicada silenciosamente.

## Divisões de validação

### Cinco folds espaciais

`fold_espacial` indica em qual das cinco rodadas uma linha de 2024 será validação. Na rodada `k`, os outros quatro folds são treino. A atribuição usa `GroupKFold(n_splits=5)`, determinístico, sem embaralhamento e procurando equilibrar o número de registros.

O grupo é o código municipal de sete dígitos da fonte. Se ele não existir nesse formato, usa-se uma célula de 0,25 grau como substituta, identificada por prefixo diferente. Não se atribui um grupo único a cada linha. Cada grupo aparece em apenas um fold de validação, e cada linha é validada uma vez.

### Cinco folds temporais progressivos

| Rodada | Treino de 2024 | Validação de 2024 |
|---|---|---|
| 0 | Janeiro–fevereiro | Março–abril |
| 1 | Janeiro–abril | Maio–junho |
| 2 | Janeiro–junho | Julho–agosto |
| 3 | Janeiro–agosto | Setembro–outubro |
| 4 | Janeiro–outubro | Novembro–dezembro |

Essa avaliação mede uma dificuldade diferente da espacial: o treino precede a validação, mas os mesmos municípios podem aparecer em ambos. Não combinar as métricas dos dois protocolos como se fossem um único experimento. Algumas linhas iniciais servem apenas para treino no protocolo temporal; não se exige que sejam validadas nele.

### Teste externo de 2025

O teste fica em arquivo separado e seu `fold_espacial` é vazio. Os mesmos municípios podem aparecer em anos diferentes: a separação externa é temporal, não uma exigência de municípios inéditos. A auditoria examina integridade e cobertura de 2025, mas omite distribuição de FRP, rótulos derivados, acurácia e demais métricas preditivas. Nenhum modelo foi treinado para esta entrega do dataset.

## Uso nos notebooks

Criar os notebooks na raiz do repositório, ao lado de `utils.py`. No ambiente Python preparado:

```python
import numpy as np
from utils import carregar_dados, iterar_folds, preparar_particao, ATRIBUTOS

np.random.seed(42)
desenvolvimento = carregar_dados(2024)  # o padrão também é 2024

for fold, treino, validacao in iterar_folds(desenvolvimento, "espacial"):
    dados = preparar_particao(treino, validacao, representacao="padronizada")
    X_treino = dados.X_treino.to_numpy()
    X_validacao = dados.X_avaliacao.to_numpy()
    y_reg_treino = dados.y_reg_treino.to_numpy()
    y_reg_validacao = dados.y_reg_avaliacao.to_numpy()
    y_cls_treino = dados.y_cls_treino.to_numpy()
    y_cls_validacao = dados.y_cls_avaliacao.to_numpy()
    # Implementar e avaliar o modelo aqui, usando os mesmos folds nas comparações.
```

Para a árvore didática, usar `representacao="discretizada"`; a matriz terá seis colunas binárias. Para regressões/logística, a forma padronizada já inclui imputação e mantém seis atributos. `numerica` oferece os valores imputados sem escala. Para validar por tempo, trocar a estratégia por `"temporal"`.

O ajuste e a avaliação finais, somente depois de encerrar as escolhas em 2024, podem preparar os dados assim:

```python
treino_final = carregar_dados(2024)
teste_final = carregar_dados(2025)
dados_finais = preparar_particao(treino_final, teste_final, "padronizada")
# Ajustar no treino_final e avaliar uma vez no teste_final.
```

`Particao` não contém um modelo treinado. O usuário implementará a árvore, regressões e demais algoritmos nos notebooks. Como a classe elevada representa aproximadamente um quarto do treino, apresentar também precisão, recall, F1 e comparação com a classe majoritária, além da acurácia pedida pelo professor.

## Ambiente e reprodução

Ambiente validado: Python **3.12.14** no macOS. As versões instaladas estão fixadas em [requirements.txt](../requirements.txt); a versão de Python está em [.python-version](../.python-version). O ambiente inclui NumPy, pandas, scikit-learn, matplotlib e JupyterLab. Não inclui os modelos que deverão ser implementados, nem as bibliotecas das etapas futuras de rede Bayesiana/fuzzy.

Com `uv` instalado, na raiz do projeto:

```sh
uv venv --python 3.12.14
uv pip sync --python .venv/bin/python requirements.txt
.venv/bin/python -m ipykernel install --prefix .venv --name fia --display-name "FIA (Python 3.12)"
.venv/bin/jupyter lab
```

Selecionar o kernel **FIA (Python 3.12)** nos notebooks. O ambiente `.venv/` fica local e não é enviado ao GitHub. Uma instalação convencional pode usar `python3.12 -m venv .venv` e instalar o mesmo `requirements.txt` com o pip desse ambiente.

Para reconstruir os produtos a partir dos originais oficiais, sem registrar novos hashes:

```sh
.venv/bin/python scripts/baixar_fontes.py --baixar
.venv/bin/python scripts/preparar_dados.py
.venv/bin/python -m unittest discover -s tests -v
```

A aquisição baixa somente originais ausentes e exige correspondência com os hashes já registrados. Uma mudança na fonte interrompe a reprodução; não atualizar hashes automaticamente para contornar a divergência. O sinalizador `--registrar-fontes` foi usado apenas na primeira aquisição e recusa sobrescrever o manifesto existente.

### Verificações executadas nesta versão

Os **11 testes passaram**: identidade e filtros, dicionário/contagens, ausências preservadas, folds espaciais sem grupos compartilhados, ordem temporal, reserva de 2025 e preparação sem parâmetros aprendidos na avaliação. Também foram verificadas a compatibilidade das 107 dependências instaladas e a execução dos exemplos no kernel FIA do Jupyter, nas três representações de X.

A reconstrução a partir dos 24 originais produziu os mesmos bytes nos dois datasets comprimidos e no registro de exclusões. Os hashes de código e as versões de Python/NumPy/pandas/scikit-learn usadas na construção estão no manifesto do dataset. Essas verificações cobrem a preparação dos dados; não são testes de desempenho de modelos.

## Limitações de interpretação

A [documentação do INPE](https://data.inpe.br/queimadas/pages/secao_informacoes/faq/index.html) distingue foco detectado de incêndio e informa limitações de observação. Este dataset contém somente detecções: não oferece observações negativas equivalentes para prever ausência ou surgimento de fogo. FRP mede potência radiativa do pixel e não área queimada, dano ambiental ou prioridade operacional comprovada.

Detecções próximas podem pertencer ao mesmo evento, mesmo com identificadores diferentes. A deduplicação exata e a divisão por município não eliminam toda dependência espacial. Nuvens, relevo e horário do sensor podem afetar o registro. O mesmo sensor reduz heterogeneidade, mas não torna todas as observações independentes. Ausências de dias sem chuva e limitações de representatividade dos meses/regiões devem ser discutidas nos resultados dos notebooks.

O [protocolo do scikit-learn](https://scikit-learn.org/stable/common_pitfalls.html) orienta que transformações aprendidas sejam ajustadas no treino. Os folds por grupo seguem a definição de [GroupKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html). As verificações de qualidade não demonstram capacidade preditiva: essa avaliação ainda pertence aos notebooks.
