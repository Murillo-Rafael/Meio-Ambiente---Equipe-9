# Análise da fonte e viabilidade

Data de acesso: **31/10/2026**. Escopo desta fase: análise descritiva e proposta de uso. Nenhum resultado preditivo foi produzido.

## 1. Pergunta aprovada

**Em focos de fogo já detectados no bioma Amazônia brasileiro, como estimar a potência radiativa e identificar a faixa de maior potência a partir de atributos meteorológicos, espaciais e temporais?**

Recorte adotado: bioma Amazônia no Brasil; sensor AQUA_M-T; 2024 para desenvolvimento; 2025 para teste; classificação pelo percentil 75 do treino. A troca da base originalmente sugerida no trabalho foi autorizada pelo professor, **segundo informação do responsável**. Não foi apresentada comprovação documental dessa autorização.

A base contém detecções positivas. O objetivo não será prever existência de fogo em locais sem observação, nem distinguir queima controlada de incêndio. A unidade é um registro de detecção em um pixel e horário, não um incêndio independente.

## 2. Fontes efetivamente inspecionadas

O [catálogo indicado](https://dados.gov.br/dados/conjuntos-dados/monitoramento-de-queimadas) requer JavaScript para leitura de seus metadados. A análise dos arquivos usou diretamente o [repositório oficial do INPE](https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/), ligado pelo próprio Programa Queimadas.

Foram baixados sete arquivos, totalizando **347.535.277 bytes**: dois ZIPs anuais e cinco CSVs mensais. URLs e hashes estão em [manifesto.json](../data/manifesto.json); as contagens completas estão em [perfil-dados.json](perfil-dados.json). O programa de auditoria usa apenas a biblioteca padrão do Python e permite reproduzir as medições.

### Esquemas diferentes: decisão baseada nos arquivos

| Produto | Conteúdo verificado | Uso no trabalho |
|---|---|---|
| Anuais Brasil/satélite de referência, 2024 e 2025 | 9 campos: identificadores, coordenadas, data, país, estado, município e bioma | Auditoria de esquema e dimensão; inadequados sozinhos para o alvo FRP |
| Mensais Brasil, meses selecionados de 2024/2025 | 16 campos, incluindo sensor, FRP, dias sem chuva, precipitação e índice de risco | Fonte principal para construir o dataset |

Os anuais contêm 278.299 registros brasileiros em 2024 e 136.393 em 2025; respectivamente 140.346 e 43.131 estão marcados como Amazônia. Essas contagens não são uma confirmação do tamanho do futuro dataset mensal: os produtos podem ter revisões distintas. O campo de sensor não está presente nesses anuais. **Não concatenar anuais e mensais**, pois isso não acrescenta observações independentes.

### Piloto: arquivos mensais completos, com filtro de sensor e bioma

| Arquivo | Registros Brasil, todos os sensores | Registros Amazônia, todos os sensores | Amazônia/AQUA_M-T | Casos completos centrais* | Dias sem chuva ausentes/inválidos |
|---|---:|---:|---:|---:|---:|
| Janeiro/2024 | 152.585 | 61.127 | 2.049 | 2.021 | 28 |
| Abril/2024 | 49.823 | 18.909 | 1.117 | 1.116 | 1 |
| Outubro/2024 | 1.006.520 | 467.435 | 16.169 | 15.869 | 300 |
| Janeiro/2025 | 63.439 | 24.237 | 1.219 | 1.194 | 25 |
| Outubro/2025 | 823.767 | 176.050 | 7.868 | 7.721 | 147 |
| **Total piloto** | **2.096.134** | **747.758** | **28.422** | **27.921** | **501** |

*FRP, dias sem chuva, precipitação e coordenadas numéricas válidas. Não inclui o índice de risco, que não é preditor principal.

No recorte AQUA_M-T/Amazônia dos cinco arquivos:

- 98,24% são casos completos centrais; FRP, precipitação e coordenadas não apresentaram ausências ou valores fora dos domínios checados.
- Não foram encontradas duplicatas por identificador nem por combinação exata de coordenadas, horário e sensor, dentro de cada arquivo.
- Houve 151 valores ausentes/inválidos no índice de risco. O campo não será usado como alvo nem como preditor principal.
- Os meses foram escolhidos para diagnosticar esquema, volume e cobertura em diferentes partes do calendário. **Não são uma amostra aleatória**, nem sustentam uma caracterização anual da Amazônia.
- A auditoria não verifica todas as possíveis inconsistências físicas, datas ou falhas de detecção. A próxima fase deverá conferir os 24 meses e duplicatas entre arquivos.

### Distribuição de FRP inspecionada somente em 2024

| Mês | Mediana (MW) | Percentil 75 (MW) | Máximo (MW) |
|---|---:|---:|---:|
| Janeiro/2024 | 17,4 | 31,3 | 1.933,8 |
| Abril/2024 | 14,7 | 28,0 | 1.782,8 |
| Outubro/2024 | 22,3 | 44,9 | 3.902,8 |

Fato observado: a distribuição tem cauda longa e o quartil superior varia entre os meses inspecionados. Hipótese a testar: regressões lineares simples podem apresentar limitações para explicar os extremos. Não há evidência de R² ou acurácia nesta fase. A FRP zero de outubro foi preservada como valor não negativo e deverá ser investigada; não foi substituída por ausência automaticamente.

Em 2025 foram inspecionados esquema, cobertura e validade, mas não os resumos dos valores de FRP, rótulos derivados ou desempenho. O ano será reservado à avaliação final, sem ajuste posterior de modelos a partir de seus resultados.

## 3. Contrato do dataset proposto

Nome de trabalho: **Focos Amazônia INPE 2024–2025**. Todas as linhas e o alvo virão do INPE. Complementos poderão acrescentar atributos com procedência explícita; não substituirão essa fonte principal.

| Campo | Origem | Papel |
|---|---|---|
| `id`, `data_hora_gmt`, `satelite`, `pais`, `bioma` | INPE | Identidade, rastreabilidade e filtros |
| `municipio_id`, `estado_id`, `municipio`, `estado` | INPE | Descrição e agrupamento da validação |
| `lat`, `lon` | INPE | Coordenadas; preditores e diagnóstico espacial |
| `numero_dias_sem_chuva`, `precipitacao` | INPE | Preditores meteorológicos |
| `mes`, `hora_utc` | Derivados do horário INPE | Preditores temporais |
| `frp` | INPE, MW | Alvo contínuo; nunca entra em X |
| `frp_elevada` | Derivado de FRP e limiar do treino | Alvo binário; nunca entra em X |
| `risco_fogo` | INPE | Contexto e auditoria; índice composto, não probabilidade aprendida |
| `arquivo_origem`, `sha256_origem`, `ano`, `particao` | Metadados derivados | Reprodução e separação experimental |

Seis atributos principais: **dias sem chuva, precipitação, latitude, longitude, mês e hora UTC**. O número de dias sem chuva e a chuva acumulada são informações associadas ao instante de detecção; o modelo será retrospectivo, condicionado à detecção, sem alegação de previsão antecipada. Identificadores, probabilidades de outros modelos e alvos derivados ficam fora desses seis preditores.

A hora UTC pode capturar aspectos da observação do sensor; sua relevância deverá ser discutida. Codificações cíclicas de mês/hora podem expandir colunas numéricas sem acrescentar atributos conceituais. A árvore didática e os cálculos probabilísticos poderão usar versões discretizadas dos mesmos atributos, com limites definidos exclusivamente no treino.

### Definição dos alvos

Regressão: `y_reg = frp`, em MW. Estimar FRP diretamente será a análise principal; `log1p(FRP)` poderá ser uma análise de sensibilidade, com métricas também na unidade original e explicação da transformação inversa.

Classificação: `tau = Q75(FRP_treino)` e `y_cls = 1[FRP >= tau]`. O percentil 75 é uma definição estatística aprovada para este trabalho, **não uma escala oficial de gravidade**. Valores empatados podem produzir mais de 25% de positivos. Na validação interna, cada fold calcula seu tau apenas com o treino e todos os classificadores usam exatamente esse mesmo tau e os mesmos exemplos. No modelo final, tau será calculado em 2024 e congelado para 2025; não haverá um novo percentil calculado no teste.

### Tratamento previsto, ainda não executado

1. Baixar os 24 CSVs mensais de 2024–2025, registrar hashes e confirmar esquema.
2. Aplicar os filtros `pais=Brasil`, `bioma=Amazônia`, `satelite=AQUA_M-T` e validar datas/identificadores/coordenadas.
3. Remover duplicatas exatas; preservar detecções próximas como registros distintos, com agrupamento para avaliar dependência.
4. Converter vazios, -999 e valores incompatíveis com o domínio em ausências; contabilizar cada exclusão. Excluir alvo ausente, sem inventar FRP.
5. Aprender imputação, escalonamento e discretização só no treino. Para os dias sem chuva, comparar imputação pela mediana de treino e análise de casos completos, sem supor ausência aleatória.
6. Gerar tabela derivada, dicionário e manifesto com contagens por filtro. Os dados brutos serão preservados localmente; não entram no Git.

## 4. Complementação confiável

O [INMET disponibiliza históricos anuais de estações automáticas](https://portal.inmet.gov.br/dadoshistoricos). Temperatura e umidade são candidatas justificáveis, mas sua qualidade espacial não foi medida nesta fase. A documentação de [FRP do NASA/FIRMS](https://firms.modaps.eosdis.nasa.gov/descriptions/FIRMS_MODIS_Firehotspots.html) complementa a interpretação das medições; não constitui uma amostra independente de focos para somar ao INPE.

Proposta técnica, ainda não validada: testar associação de cada foco à estação operacional mais próxima, com limite inicial de 50 km, usando somente medições anteriores ou iguais ao horário da detecção. Registrar estação, distância, horário, quantidade de observações válidas e cobertura. O limite de 50 km é uma hipótese operacional a submeter a sensibilidade, não garantia de representatividade meteorológica.

Só promover temperatura/umidade ao modelo principal se a auditoria mostrar pelo menos 80% de associações válidas em cada ano e não revelar seleção espacial problemática. Esse percentual é um critério de projeto proposto, não resultado observado. Caso contrário, manter os seis atributos INPE e apresentar o complemento como análise restrita. Se aprovado tecnicamente, substituir longitude e hora por temperatura e umidade para continuar com seis atributos; comparar as configurações na validação de 2024, nunca por ajuste ao teste de 2025.

## 5. Limites e conclusão de viabilidade

A FRP é potência radiativa de um pixel; não mede diretamente área queimada, dano à biodiversidade ou necessidade de combate. Um incêndio pode gerar muitos registros e um pixel pode conter múltiplas frentes. Nuvens, horário e características do sensor afetam a detecção; usar um único sensor reduz uma fonte de heterogeneidade, sem eliminar esses efeitos.

**Viável para as seis etapas acadêmicas**, pois os arquivos mensais inspecionados oferecem alvo contínuo, rótulo binário derivável e atributos interpretáveis. O suporte preditivo desses atributos continua desconhecido. Não será legítimo ajustar dados ou escolher um recorte para atingir as faixas de desempenho ilustradas no PDF.

A construção e auditoria dos 24 meses ainda estão pendentes. Os resultados aqui apresentados se limitam aos arquivos do piloto.
