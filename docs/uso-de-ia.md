# Registro de uso de IA: análise e planejamento

Data: **31/10/2026**. Assistente utilizado: Codex. Este registro documenta as solicitações humanas desta fase e as decisões que orientaram a entrega. Novas solicitações de implementação deverão ser acrescentadas quando ocorrerem.

## Solicitação original

```text
/goal # PAPEL

Você é um cientista de dados formado em harvard com pós graduação em engenharia florestal, com experiência em times que monitoram focos de queimada na região da amazonia.

# MISSÃO

Sua missão é desenvolver o que se pede no trabalho, vamos usar u conjunto de dados diferente do do link da especificação mas foi autorizdo pelo professor.

O resultado deve permitir entregar o repositório completo, com tudo o que se pede

# MATERIAL DE REFERÊNCIA

https://dados.gov.br/dados/conjuntos-dados/monitoramento-de-queimadas

Utilize esse material como referência para executar a tarefa, junto com o pdf anexado.

# INSTRUÇÕES

Execute a tarefa seguindo estas etapas:

1. Análise: Analise o conjunto de dados e idealize como ele pode ser usado no trabalho
2. Planejamento: leia atentamente todas as etapas do trabalho, crie um repositório no github para organizar a entra
3. Execução: Voce sepre deve executar uma etapa de cada vez
4. Validação: faça sua analise com base em dados, validação humana só na entrega final

# REGRAS

- Siga rigorosamente as instruções fornecidas.
- Priorize informações precisas, verificáveis e relevantes.
- Não invente informações, dados ou referências.
- Diferencie fatos confirmados de hipóteses e suposições.
- Utilize linguagem clara, objetiva e adequada ao público-alvo.
- Evite explicações redundantes e conteúdo fora do escopo.
- Quando for escrever os programas, sempre não faça um commit apenas no final, divida as subtarefas por commits, assinados em meu nome e com mensagens atomicas e em portugues.

# CRITÉRIOS DE DECISÃO

Quando houver múltiplas alternativas:

1. Priorize interpretar o que esta escrito na especificação do trabalho.
2. Considere o contexto do tema que estamos trabalhando
3. Avalie a veracidade dos fatos
4. Justifique escolhas relevantes com base nos critérios definidos.

# FALLBACK

Caso existam informações insuficientes, ambiguidades ou limitações:

- Utilize o contexto disponível antes de solicitar esclarecimentos.
- Faça suposições razoáveis apenas quando não comprometerem o resultado, identificando-as explicitamente.
- Solicite informações adicionais somente quando forem indispensáveis.
- Se uma etapa não puder ser concluída, explique a limitação e apresente o resultado parcial possível.

# TAREFA

Realizar as etapas um e dois, quero que me pergunte decisões críticas via human in the loop, vamos fazer isso juntos
```

Anexo: `2o-Trab-SimbML-Incerteza.pdf`. A formatação de espaços e marcadores foi normalizada nesta transcrição; o conteúdo da solicitação foi preservado.

## Orientações adicionais do responsável

```text
A gente pode buscar dados de outras fontes desde que sejam fontes relevantes e confiáveis
```

```text
vamos tentar usar a maioria do link que eu mandei ok? mas pode complementar. a gente onta um dataset para esse trabalho
```

Ao discutir percentil 75 e mediana, o responsável solicitou:

```text
No que isso implica? eu quero entender melhor a diferença
```

Foi explicado que Q75 destaca aproximadamente um quarto das observações de treino, enquanto a mediana divide aproximadamente em metades; empates alteram proporções; o limiar será congelado para o teste. Também se explicou o baseline de maioria e que o rótulo não representa gravidade ambiental.

## Respostas às decisões críticas

| Tema apresentado pelo assistente | Escolha humana |
|---|---|
| Potência de focos detectados vs. previsão de novas ocorrências | Potência dos focos detectados |
| Bioma Amazônia vs. estado do Amazonas vs. Amazônia Legal | Bioma Amazônia no Brasil |
| Dois anos com teste externo vs. um ano com divisão interna | 2024 desenvolvimento e 2025 teste, sensor AQUA_M-T |
| Percentil 75 vs. mediana, após explicação | Percentil 75: destacar o quarto de maior potência |

## Contribuição da IA e evidência independente

A IA auxiliou na leitura dos requisitos, busca de fontes oficiais, elaboração de um programa de auditoria descritiva, análise dos arquivos, documentação do contrato de dados e planejamento dos seis módulos. A análise numérica foi executada sobre arquivos oficiais com hashes registrados, não gerada por estimativa textual.

Nenhum algoritmo acadêmico foi implementado ou treinado nesta fase. Não existem métricas preditivas, revisão técnica por especialista ou validação operacional para relatar. Durante a execução, registrar prompts adicionais, alterações humanas e verificações realizadas; no relatório, incluir apêndice compacto com referência a este arquivo, respeitando 6–8 páginas.

## Construção do dataset e preparação dos notebooks

Solicitação adicional do responsável em 31/10/2026:

```text
Por favor favor, contrói e audita esse dataset para que eu possa implementar os notebooks, cria um documento auxiliar explicando o dataset.
```

O trecho selecionado para contexto pedia construir e auditar o dataset completo de 2024–2025, preparar o tratamento de ausências, as divisões de validação e o ambiente reproduzível. Foi mantida a orientação de publicar no GitHub somente os materiais acadêmicos e os necessários à reprodução.

A IA auxiliou na aquisição dos 24 arquivos oficiais, filtragem Brasil/Amazônia/AQUA_M-T, preservação de ausências, rastreabilidade e preparação dos folds/transformações. Produziu funções auxiliares de leitura/preparação, testes, ambiente com versões fixadas, dicionário e guia explicativo. As decisões de fonte, anos, sensor, atributos e quartil superior foram preservadas.

O resultado contém 140.346 registros de desenvolvimento e 43.131 de teste. Foram executados 11 testes, conferência agregada com os produtos anuais do próprio INPE, reconstrução idêntica dos CSVs comprimidos e execução dos exemplos no kernel Jupyter. Não foram implementados os notebooks acadêmicos, ajustados modelos ou calculadas métricas preditivas de 2025; essa parte permanece sob execução do responsável.
