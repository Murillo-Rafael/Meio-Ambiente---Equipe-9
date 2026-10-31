# Fontes e evidências

Acesso em **31 out. 2026**. Prioridade: especificação do professor, registros oficiais do INPE e, para eventuais complementos, fontes primárias confiáveis. Afirmações do responsável, decisões metodológicas e hipóteses são identificadas nos documentos.

| Fonte | Evidência usada | Situação |
|---|---|---|
| PDF `2o-Trab-SimbML-Incerteza.pdf`, Prof. Edjard Mota, 15/10/2026, 10 páginas | Requisitos, rubrica, entregáveis e cronograma | Lido integralmente; páginas 3, 4 e 10 também renderizadas e inspecionadas. Hash em `data/manifesto.json`; original fornecido pelo responsável, não redistribuído |
| [Catálogo Dados.gov.br indicado pelo responsável](https://dados.gov.br/dados/conjuntos-dados/monitoramento-de-queimadas) | Ponto de partida temático | A página exige JavaScript; os metadados não foram recuperados pelo leitor web |
| [Dados abertos do Programa Queimadas/INPE](https://data.inpe.br/queimadas/dados-abertos/) | Produtos e acesso oficial | Consultado |
| [CSV anuais de referência](https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/anual/Brasil_sat_ref/) | Disponibilidade 2024/2025; auditoria de esquema e contagens | Dois arquivos íntegros auditados |
| [CSV mensais Brasil](https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/mensal/Brasil/) | Disponibilidade histórica e fonte principal do dataset | Cinco arquivos íntegros auditados; os outros meses ainda não foram baixados |
| [Perguntas frequentes do INPE](https://data.inpe.br/queimadas/pages/secao_informacoes/faq/index.html), questões 7, 10, 11, 23 e 42–44 | Definições de foco, sensor, campos e limites da FRP | Consultado; partes históricas da página têm referências de épocas diferentes, portanto o esquema efetivo foi checado nos arquivos |
| [NASA/FIRMS: descrição dos campos MODIS](https://firms.modaps.eosdis.nasa.gov/descriptions/FIRMS_MODIS_Firehotspots.html) | FRP em MW e natureza da medição por pixel | Documentação complementar; sem inclusão de novas linhas no dataset |
| [INMET: dados históricos anuais](https://portal.inmet.gov.br/dadoshistoricos) | Disponibilidade de pacotes de estações automáticas para 2024 e 2025 | Catálogo consultado; dados de estações não baixados, cobertura de associação ainda não medida |
| [INMET: BDMEP](https://portal.inmet.gov.br/servicos/bdmep-dados-historicos) | Natureza das séries diárias de estações convencionais | Alternativa oficial avaliada; não selecionada para ingestão nesta fase |

As estatísticas em `analise-dados.md` foram calculadas diretamente dos arquivos oficiais, não copiadas de resultados de busca. URLs individuais, bytes e SHA-256 estão no manifesto; `perfil-dados.json` é a evidência legível por máquina.

## Referências acadêmicas previstas pelo PDF

- Russell, S.; Norvig, P. *Artificial Intelligence: A Modern Approach*. 4ª ed. Pearson, 2020, capítulos 18–20.
- Zadeh, L. A. Fuzzy sets. *Information and Control*, 8(3), 338–353, 1965.
- Hüllermeier, E. Fuzzy machine learning and data mining. *WIREs Data Mining and Knowledge Discovery*, 1(4), 269–283, 2011.

Os três registros acima foram transcritos da bibliografia da especificação; o conteúdo das obras não foi examinado nesta fase. Na elaboração do relatório, confirmar metadados e citar apenas o conteúdo efetivamente consultado.
