# Fundamentos de IA: focos de fogo no bioma Amazônia

Trabalho integrado **Do Simbólico à Incerteza**, Prof. Edjard Mota, especificação de 15/10/2026.

O projeto estuda a potência radiativa (FRP) de focos **já detectados** no bioma Amazônia brasileiro. A fonte principal é o Programa Queimadas do INPE, a partir do [catálogo indicado](https://dados.gov.br/dados/conjuntos-dados/monitoramento-de-queimadas).

## Estado atual

**Etapas do projeto concluídas: análise e planejamento.** Nenhum modelo foi implementado ou treinado. O dataset integral, os seis notebooks, o relatório e a apresentação pertencem à execução futura.

Decisões confirmadas: recorte do bioma Amazônia no Brasil, sensor AQUA_M-T, desenvolvimento em 2024 e teste em 2025. A classificação destacará FRP igual ou superior ao percentil 75 do treino, com limiar congelado no teste. Esse rótulo é estatístico, sem equivalência automática com gravidade ambiental. O repositório é privado.

## Documentação

| Documento | Conteúdo |
|---|---|
| [Análise dos dados](docs/analise-dados.md) | Auditoria, limitações, atributos, alvos e contrato do dataset |
| [Requisitos do PDF](docs/requisitos.md) | Todas as seis etapas, entregáveis, rubrica e evidências previstas |
| [Plano de execução](docs/plano.md) | Sequência de trabalho, validação, estrutura futura e commits |
| [Decisões](docs/decisoes.md) | Escolhas aprovadas pelo responsável e pendências delimitadas |
| [Fontes](docs/fontes.md) | Fontes oficiais e distinção entre consultado e ainda não verificado |
| [Uso de IA](docs/uso-de-ia.md) | Solicitações e decisões para o futuro apêndice |
| [Manifesto](data/manifesto.json) e [perfil dos dados](docs/perfil-dados.json) | URLs, hashes e resultados calculados da auditoria |

## Evidência da análise

Sete arquivos oficiais auditados: dois anuais e cinco mensais. Os anuais verificados não oferecem FRP e meteorologia; os mensais serão a fonte de modelagem. Nos cinco meses inspecionados, o recorte Amazônia/AQUA_M-T contém **28.422 registros**, dos quais **27.921 (98,24%)** têm FRP, meteorologia central e coordenadas completas. Os meses são um piloto de cobertura, não uma amostra anual aleatória.

Todas as linhas e o alvo do dataset virão do INPE. Dados do INMET poderão complementar atributos se uma avaliação de cobertura e qualidade justificar sua inclusão. A associação com estações ainda não foi realizada.

## Reproduzir a auditoria atual

Requer Python **3.11 ou superior**, sem dependências externas. Na raiz do projeto:

```sh
python3 scripts/analisar_fontes.py --baixar
```

O comando obtém aproximadamente 348 MB de originais quando ausentes, valida SHA-256 e regenera `docs/perfil-dados.json`. Para usar somente os arquivos locais, omitir `--baixar`. Detalhes em [data/README.md](data/README.md). `data/raw/` e `data/processed/` são locais e ficam fora do Git; a reprodução é feita a partir das fontes e do manifesto.

As instruções de execução dos modelos e de compilação do artigo serão adicionadas quando esses artefatos existirem. O próximo pacote é **montar e auditar o dataset completo de 2024–2025**, antes da árvore de decisão.

## Histórico e autoria

Commits atômicos em português, com autoria **Matheus Garcia** e `Signed-off-by`, conforme autorizado. Esse registro de autoria não equivale a assinatura criptográfica. A sequência futura de commits está no plano; não concentrar a implementação em um único commit ao final.
