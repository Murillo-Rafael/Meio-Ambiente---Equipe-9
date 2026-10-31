# Fundamentos de IA: focos de fogo no bioma Amazônia

Trabalho integrado **Do Simbólico à Incerteza**, Prof. Edjard Mota, especificação de 15/10/2026.

O projeto estuda a potência radiativa (FRP) de focos **já detectados** no bioma Amazônia brasileiro. A fonte principal é o Programa Queimadas do INPE, a partir do [catálogo indicado](https://dados.gov.br/dados/conjuntos-dados/monitoramento-de-queimadas).

## Estado atual

**Dataset construído e auditado para implementar os notebooks.** Os arquivos de desenvolvimento (2024) e teste (2025), a preparação dos atributos e as divisões de validação estão disponíveis. Os seis notebooks, os modelos acadêmicos, o relatório final e a apresentação ainda serão produzidos.

Recorte metodológico: bioma Amazônia no Brasil, sensor AQUA_M-T, desenvolvimento em 2024 e teste em 2025. A classificação destacará FRP igual ou superior ao percentil 75 do treino, com limiar congelado no teste. Esse rótulo é estatístico, sem equivalência automática com gravidade ambiental.

## Documentação

| Documento | Conteúdo |
|---|---|
| [Guia do dataset](docs/dataset.md) | Explicação do dataset, limpeza, atributos, alvos, ambiente e exemplos de uso nos notebooks |
| [Dicionário](data/dicionario.csv) | Tipos, unidades, origem e papel das 27 colunas |
| [Auditoria completa](docs/auditoria-dataset.json) | Cobertura, filtragem, ausências e cinco folds espaciais/temporais |
| [Fontes de 2024–2025](data/fontes_2024_2025.json) e [produtos](data/dataset/manifesto.json) | URLs, hashes e contagens do dataset integral |
| [Análise inicial dos dados](docs/analise-dados.md) | Estudo anterior de viabilidade com cinco meses, preservado como referência |
| [Fontes](docs/fontes.md) | Fontes oficiais e distinção entre consultado e ainda não verificado |
| [Uso de IA](docs/uso-de-ia.md) | Registro de prompts e escolhas metodológicas para o apêndice exigido |

## Dados prontos para os notebooks

- [Desenvolvimento de 2024](data/dataset/desenvolvimento_2024.csv.gz): usar para implementar, comparar e selecionar modelos.
- [Teste de 2025](data/dataset/teste_2025.csv.gz): reservar para a avaliação final, após encerrar escolhas em 2024.

**140.346 registros em 2024** e **43.131 em 2025**, em dois CSVs comprimidos que somam aproximadamente 8,89 MB. Os dois arquivos derivados estão no GitHub. Eles contêm todas as detecções válidas do recorte nos 24 meses, sem amostragem. Os originais maiores ficam fora do Git e podem ser obtidos pelo manifesto. Esta versão utiliza somente o INPE, inclusive para os atributos meteorológicos; não houve associação com estações externas.

## Ambiente e início rápido

Ambiente validado: **Python 3.12.14**. Na raiz do projeto, com `uv`:

```sh
uv venv --python 3.12.14
uv pip sync --python .venv/bin/python requirements.txt
.venv/bin/python -m ipykernel install --prefix .venv --name fia --display-name "FIA (Python 3.12)"
.venv/bin/jupyter lab
```

Usar o kernel **FIA (Python 3.12)**. Para ler e preparar uma divisão, sem treinar modelos:

```python
from utils import carregar_dados, iterar_folds, preparar_particao

dados = carregar_dados(2024)
fold, treino, validacao = next(iterar_folds(dados, "espacial"))
particao = preparar_particao(treino, validacao, "padronizada")
X_treino = particao.X_treino
y_reg_treino = particao.y_reg_treino
y_cls_treino = particao.y_cls_treino
```

A imputação, a padronização e o Q75 são calculados somente no treino da divisão. Para a árvore didática, usar `"discretizada"`; para valores sem padronização, `"numerica"`. O [guia](docs/dataset.md) explica os alvos, as duas estratégias de validação e os limites de interpretação.

## Reconstruir e verificar

```sh
.venv/bin/python scripts/baixar_fontes.py --baixar
.venv/bin/python scripts/preparar_dados.py
.venv/bin/python -m unittest discover -s tests -v
```

O primeiro comando baixa somente os originais ausentes e confere os hashes dos 24 meses. O segundo reconstrói as tabelas e a auditoria, sem ajustar modelos. Os testes verificam qualidade, separações espaciais/temporais e ausência de vazamento na preparação. Detalhes em [data/README.md](data/README.md).

As instruções de execução dos modelos e de compilação do artigo serão adicionadas quando esses artefatos existirem.

## Histórico e autoria

Autoria: **Matheus Garcia**. O histórico registra contribuições incrementais com `Signed-off-by`.
