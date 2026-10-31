# Dados

O dataset será construído a partir dos CSVs mensais oficiais do Programa Queimadas/INPE, mantendo o bioma Amazônia no Brasil e o sensor AQUA_M-T. Desenvolvimento: 2024. Teste: 2025. A construção completa ainda não foi executada.

- `manifesto.json`: sete arquivos efetivamente auditados, com URL, bytes e SHA-256; não é uma lista de todos os arquivos da futura ingestão.
- `raw/`: originais baixados, ignorados pelo Git. Aproximadamente 348 MB em unidades decimais no piloto atual.
- `processed/`: destino previsto da tabela derivada, também ignorado pelo Git.
- `../docs/perfil-dados.json`: auditoria reproduzível dos arquivos selecionados.

## Reproduzir a auditoria

Requer Python **3.11 ou superior**, sem pacotes externos. A partir da raiz do repositório:

```sh
python3 scripts/analisar_fontes.py --baixar
```

O programa baixa somente arquivos do manifesto que estiverem ausentes, confere os hashes e regenera `docs/perfil-dados.json`. Uma divergência de hash interrompe a execução: é necessário reauditar a revisão da fonte antes de alterar o manifesto. Para verificar arquivos locais, omitir `--baixar`.

O programa não extrai ZIPs no sistema de arquivos e não ajusta modelos. As estatísticas de valores FRP de 2025 são omitidas intencionalmente; cobertura e validade são auditadas.

O esquema, os filtros, o tratamento de ausências, a definição do alvo e as regras para possíveis complementos estão em [Análise dos dados](../docs/analise-dados.md).
