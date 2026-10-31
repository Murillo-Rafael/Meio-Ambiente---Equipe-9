# Registro de decisões

Data: **31/10/2026**. As decisões abaixo foram discutidas com o responsável durante análise e planejamento.

| ID | Decisão | Situação e motivo |
|---|---|---|
| D01 | Estimar potência de focos detectados, em vez de prever existência futura de fogo | **Aprovada pelo responsável.** A base de focos não fornece observações negativas equivalentes |
| D02 | Recorte: bioma Amazônia no território brasileiro | **Aprovada.** Não confundir com estado do Amazonas ou Amazônia Legal |
| D03 | Repositório `mh131105/fia-queimadas-amazonia`, privado | **Aprovada e executada.** A publicação pública não foi autorizada |
| D04 | Commits com autoria Matheus Garcia `<matheus.garcia@icomp.ufam.edu.br>` e `Signed-off-by` | **Aprovada.** Assinatura criptográfica não é exigida; commits atômicos em português |
| D05 | Manter INPE como fonte principal; complementação confiável permitida | **Instrução direta.** Todas as linhas e os alvos vêm do INPE; complementos acrescentam atributos rastreáveis |
| D06 | Usar CSVs mensais, não anuais de referência, para construir os dados | **Decisão técnica baseada em auditoria.** Os anuais verificados não contêm FRP e meteorologia |
| D07 | Sensor único AQUA_M-T; 2024 desenvolvimento, 2025 teste | **Aprovada.** Controlar uma fonte de diferenças de medição e avaliar generalização entre anos |
| D08 | FRP elevada: valor >= Q75 do treino | **Aprovada após explicação da alternativa mediana.** Destacar a faixa superior; rótulo estatístico sem escala oficial de gravidade |
| D09 | Baseline de maioria e métricas de positivos além da acurácia | **Decisão técnica.** Com Q75, acertar só a maioria pode render cerca de 75% de acurácia |
| D10 | Fontes extras: considerar INMET; NASA/FIRMS como apoio conceitual | **Proposta técnica condicional.** Associação de estações ainda não medida; não tratar detecções NASA/INPE como amostras independentes |
| D11 | Concluir nesta rodada apenas análise e planejamento | **Solicitação direta.** Construção integral do dataset e algoritmos ficam para execução futura |

## Pendências delimitadas

- Auditar os 24 meses; verificar revisões, cobertura anual e compatibilidade entre os produtos do INPE.
- Medir cobertura e qualidade da associação com INMET antes de decidir se entra no modelo principal. Não há previsão de ganho comprovado.
- Fechar versões das bibliotecas ao criar e validar o ambiente de modelagem. Nesta fase a auditoria usa Python >= 3.11 e não exige pacotes externos.
- Confirmar participantes, eventual identificador da equipe e data absoluta de entrega antes de finalizar capa e agenda. Isso não impede o planejamento relativo nem a criação do repositório.
- Conferir, na entrega final, reprodução, artigo, apresentação e compreensão dos resultados pelo responsável.

Nenhuma pendência acima justifica inventar dados, atribuir avaliações humanas inexistentes ou apresentar um modelo ainda não executado como concluído.
