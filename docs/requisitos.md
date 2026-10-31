# Matriz de requisitos da especificação

Documento de referência: *Trabalho Integrado de Fundamentos de IA — Do Simbólico à Incerteza*, Prof. Edjard Mota, 15/10/2026, 10 páginas. O hash do PDF fornecido consta em `data/manifesto.json`.

**Estado de todos os itens técnicos abaixo: planejados, não implementados.** A análise de viabilidade não substitui a entrega acadêmica. As “etapas 1 e 2” solicitadas nesta rodada são análise e planejamento do projeto; as seis etapas nesta matriz são as etapas técnicas do PDF.

## Escopo e entregáveis gerais

| ID | Exigência do PDF | Página | Evidência prevista na entrega |
|---|---|---:|---|
| G01 | Percorrer as seis etapas no mesmo domínio de dados oficiais | 3 | Dataset único e contrato consistente de alvos/splits |
| G02 | Saída Bayesiana da etapa 5 alimentar sistema fuzzy da etapa 6 | 3, 8–9 | Execução de ponta a ponta e diagrama |
| G03 | Repositório GitHub com notebooks por etapa, nomeados `etapa1.ipynb` etc. | 3–4 | Seis notebooks executados, incluindo resultados e narrativa |
| G04 | Relatório LaTeX, artigo de 6–8 páginas | 4 | Fontes e PDF compilado; comprovar contagem de páginas |
| G05 | Scripts auxiliares `utils.py`, `em.py`, `fuzzy.py` | 4 | Implementações reutilizadas pelos notebooks |
| G06 | README com instruções de reprodução | 4 | Instalação, obtenção dos dados, ordem de execução e geração do relatório |
| G07 | Documentar prompts no apêndice; compreender cada implementação | 9 | Registro de uso de IA e apêndice; explicações matemáticas e técnicas |
| G08 | Seed fixa, explicitamente `np.random.seed(42)` | 9 | Configuração comum e todos os componentes aleatórios controlados |
| G09 | Nunca reportar apenas acurácia de treino | 9 | Validação cruzada e teste externo por ano |
| G10 | Citar portal, ano da consulta e data de acesso | 10 | Bibliografia e manifesto de proveniência |
| G11 | Narrativa de 2–3 parágrafos por etapa: o quê, por quê, aprendizado | 10 | Texto nos notebooks e síntese no artigo |
| G12 | Decisão final interpretável por especialista | 9–10 | Probabilidades, regras ativadas e justificativa da prioridade acadêmica |
| G13 | Checkpoint intermediário no GitHub e apresentação final de 10 min/equipe | 3, 10 | Histórico incremental e material da apresentação |

O PDF sugere desmatamento + INMET para Meio Ambiente. A substituição por queimadas foi autorizada, segundo o responsável; essa informação não dispensa nenhum requisito técnico. Não se presume aprovação de resultados ou interpretação de modelos pelo professor.

## Etapa técnica 1: aprendizado simbólico

Peso: **12%**. Páginas 4–5.

| ID | Exigência | Aplicação e evidência previstas |
|---|---|---|
| E1.1 | Definir alvo binário ou multiclasse | FRP elevada segundo Q75 do treino |
| E1.2 | Selecionar 4–6 atributos interpretáveis | Seis atributos INPE explicitados na análise; eventual substituição por complemento documentada |
| E1.3 | Calcular manualmente entropia e ganho nos três primeiros níveis, no relatório | Tabela com contagens, proporções, H e ganhos, níveis raiz/filhos/netos; sem substituir pela saída de biblioteca |
| E1.4 | Implementar LEARN-DECISION-TREE do zero | Árvore com critérios de parada, maioria e tratamento de valores não vistos |
| E1.5 | Comparar com `DecisionTreeClassifier` | Mesmos dados e pré-processamento; `criterion='entropy'`; diferenças entre ID3 e divisões binárias discutidas |
| E1.6 | Validação cruzada 5-fold e acurácia média | Cinco folds agrupados por município em 2024; média e dispersão, além de métricas de desequilíbrio |
| E1.7 | Meia página sobre monotonicidade e exemplo novo que invalida conclusão anterior | Demonstração de revisão da regra aprendida, distinguindo atualização indutiva da monotonicidade da lógica clássica |

## Etapa técnica 2: aprendizado linear

Peso: **15%**. Página 5. A descrição geral menciona L1 ou L2, mas a tarefa específica exige **L2/Ridge**, que será seguida.

| ID | Exigência | Aplicação e evidência previstas |
|---|---|---|
| E2.1 | Alvo contínuo | FRP em MW |
| E2.2 | Linear univariada por fórmula fechada | FRP vs. dias sem chuva; coeficientes e caso de variância nula |
| E2.3 | Multivariada com gradiente descendente do zero | Mesmos atributos principais; padronização só no treino e curva de perda |
| E2.4 | Ridge e curva coeficientes vs. lambda | Intercepto sem penalização; lambda escolhido na validação de 2024 |
| E2.5 | Logística com sigmoide + gradiente, para a classe da etapa 1 | Comparação sob os mesmos folds e limiares de FRP |
| E2.6 | Comparar com `LinearRegression` e `LogisticRegression` | Métricas e coerência dos objetivos; adicionalmente Ridge como conferência da regularização |

## Etapa técnica 3: probabilidade

Peso: **10%**. Página 6.

| ID | Exigência | Aplicação e evidência previstas |
|---|---|---|
| E3.1 | Duas variáveis binárias, conjunta e quatro eventos atômicos | FRP elevada e estiagem prolongada; limiar de estiagem definido no treino e explicitado |
| E3.2 | Marginais e condicionais | Tabelas com contagens e denominadores, soma conjunta igual a 1 |
| E3.3 | Regra da cadeia para três variáveis | Acrescentar chuva baixa, com categorias definidas no treino |
| E3.4 | Bayes em caso real | P(FRP elevada | estiagem); cálculo com frequências observadas, sem inventar probabilidades |
| E3.5 | Independência condicional entre dois atributos dada a classe | Examinar chuva e dias sem chuva dado FRP elevada; não presumir independência |
| E3.6 | Interpretação causal vs. diagnóstica e limite da LPO para probabilidade | Texto explícito; associação não prova causalidade |

## Etapa técnica 4: aprendizado probabilístico e EM

Peso: **18%**. Páginas 6–7.

| ID | Exigência | Aplicação e evidência previstas |
|---|---|---|
| E4.1 | MLE de Bernoulli | Proporção de FRP elevada no treino |
| E4.2 | MAP com prior Beta | Beta(2,2), estimativa derivada e comparação com MLE |
| E4.3 | Naive Bayes do zero para a classe da etapa 1 | Treino e teste, log-probabilidades e hipóteses declaradas |
| E4.4 | Variável oculta Z com 2 ou 3 componentes; implementar EM | K=2, mistura de distribuições condicionada à classe; Z sem interpretação ecológica presumida |
| E4.5 | Curva de log-verossimilhança por iteração | Crescimento dentro de tolerância numérica e critério de convergência |
| E4.6 | Comparar NB puro e NB com EM | Mesmos dados/folds; comparar qualidade e custo, sem prometer melhora |

## Etapa técnica 5: rede Bayesiana

Peso: **18%**. Páginas 7–8.

| ID | Exigência | Aplicação e evidência previstas |
|---|---|---|
| E5.1 | DAG com 4–6 nós e justificativa de cada aresta | Seis nós: cinco variáveis do domínio e decisão da árvore obtida fora da amostra; hipótese de dependência, não causalidade demonstrada |
| E5.2 | CPTs estimadas dos dados | Contagens, normalização e suavização quando necessária |
| E5.3 | Inferência por enumeração do zero | Consultas sobre FRP elevada dadas evidências |
| E5.4 | Comparar com `pgmpy.VariableElimination` | Mesma rede e mesmas CPTs; igualdade dentro de tolerância |
| E5.5 | Duas independências por d-separação | Demonstração gráfica e confronto com dados, com possível revisão antes do teste externo |
| E5.6 | Contar economia de parâmetros vs. conjunta | Calcular pela estrutura efetivamente usada |
| E5.7 | Demonstrar um colisor que abre caminho quando observado | Exemplo derivado do DAG escolhido e sua interpretação |

## Etapa técnica 6: fuzzy e integração

Peso: **15%**. Páginas 8–9.

| ID | Exigência | Aplicação e evidência previstas |
|---|---|---|
| E6.1 | Duas ou três variáveis linguísticas | Posterior da rede Bayesiana, posterior NB/EM e prioridade de inspeção acadêmica |
| E6.2 | Pertinências triangulares | Funções com sobreposição e cobertura dos domínios |
| E6.3 | Três a cinco regras Se–Então com E/OU | Regras legíveis, explicitamente propostas pelos autores |
| E6.4 | Mamdani com `scikit-fuzzy` | Inferência e desfuzzificação, sem áreas do domínio sem saída |
| E6.5 | Probabilidade da etapa 5 como entrada | Ligação executável; usar posterior aprendido, sem confundir com `risco_fogo` do INPE |
| E6.6 | Comparar decisão fuzzy com hard threshold 0,5 | Mesmos casos; mostrar score contínuo e mudanças de decisão |
| E6.7 | Discutir interpretabilidade e fronteiras ruidosas | Casos representativos e explicação das regras |
| E6.8 | Diagrama final e reuso das etapas anteriores | Decisão da árvore como evidência da rede; posterior da rede e posterior NB/EM alimentam fuzzy |

## Rubrica e interpretação de ambiguidades

As etapas somam 88%; relatório, notebooks limpos e GitHub valem **7%**; apresentação final vale **5%**, totalizando 100% (p. 10).

As faixas do “gabarito esperado” não são resultados medidos desta base nem metas que justifiquem selecionar dados a posteriori. Isso vale para acurácia, R², profundidade, ganho com EM e 15–30 iterações. Reportar os resultados observados e explicar divergências.

O cronograma resumido (p. 3) coloca etapas 1–2 na semana 1; o detalhado (p. 10) inicia a etapa 2 na semana 1 e a conclui na semana 2. O plano segue o detalhado e registra esta diferença. O PDF não informa uma data absoluta de entrega; não se presume que o dia da publicação seja o início do prazo.

O relatório deverá manter 6–8 páginas. Como a especificação também exige apêndice de prompts e não exclui apêndices da contagem, a interpretação conservadora é incluí-lo nesse limite; manter o registro integral de prompts no repositório e apresentar no artigo um apêndice compacto com referência ao registro. Não presumir permissão para exceder oito páginas.
