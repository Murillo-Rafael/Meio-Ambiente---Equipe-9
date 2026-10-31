# Dados

Dataset construído a partir dos 24 CSVs mensais oficiais do Programa Queimadas/INPE, mantendo o bioma Amazônia no Brasil e o sensor AQUA_M-T. Desenvolvimento: 2024. Teste: 2025. O [guia do dataset](../docs/dataset.md) explica o conteúdo e seu uso nos notebooks.

- `fontes_2024_2025.json`: os 24 originais utilizados na construção integral, com URLs, bytes e SHA-256.
- `dataset/desenvolvimento_2024.csv.gz` e `dataset/teste_2025.csv.gz`: tabelas derivadas versionadas, prontas para leitura pelo pandas.
- `dataset/manifesto.json`: hashes, contagens dos produtos e contrato dos alvos.
- `dataset/exclusoes.csv.gz`: rastreabilidade das exclusões por qualidade/deduplicação, quando houver.
- `dicionario.csv`: definição das 27 colunas.
- `raw/`: originais baixados, ignorados pelo Git.
- `processed/`: reservado a resultados de trabalho locais, ignorado pelo Git; não é o diretório dos produtos entregues.
- `../docs/auditoria-dataset.json`: auditoria completa dos 24 meses.
- `manifesto.json` e `../docs/perfil-dados.json`: manifesto e auditoria históricos do piloto anterior de sete arquivos, separados da versão integral.

## Usar os dados entregues

No ambiente instalado conforme o README principal, os produtos já versionados podem ser lidos sem baixar os originais:

```python
from utils import carregar_dados
desenvolvimento = carregar_dados(2024)
```

As ausências permanecem nos CSVs. Usar `preparar_particao` para imputar/padronizar e construir o alvo binário a partir apenas do treino corrente. Não calcular previamente o Q75 sobre 2024 e 2025 juntos, nem usar um rótulo global em todos os folds.

## Reconstruir a versão integral

```sh
.venv/bin/python scripts/baixar_fontes.py --baixar
.venv/bin/python scripts/preparar_dados.py
.venv/bin/python -m unittest discover -s tests -v
```

A aquisição verifica cada SHA-256 e não atualiza o manifesto. Se o arquivo oficial mudou, a execução falha para exigir uma nova auditoria da revisão. Os arquivos existentes não são baixados novamente. O primeiro registro de hashes já foi realizado; `--registrar-fontes` recusa substituir o manifesto existente.

A construção registra os filtros/exclusões, preserva origem por linha e gera cinco folds espaciais e cinco temporais usando somente 2024. As estatísticas dos valores FRP de 2025 são omitidas; integridade e cobertura são verificadas. Nenhum modelo acadêmico é treinado.

## Auditoria histórica do piloto

O programa anterior `scripts/analisar_fontes.py --baixar` permanece disponível para reproduzir o piloto de sete arquivos, com Python >= 3.11 e sem pacotes externos. Ele escreve `docs/perfil-dados.json`, sem substituir a auditoria integral nem os produtos entregues.
